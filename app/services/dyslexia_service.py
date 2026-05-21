import json
import logging
import os
from datetime import datetime

import numpy as np

from app.ml.loaders import get_dyslexia_bundle
from app.ml.schemas import FEATURE_ORDER, ML_CLASS_TO_APP_RISK

logger = logging.getLogger(__name__)


def calculate_accuracy(recognized_text, target_text):
    if not recognized_text or not target_text:
        return 0.0
    recognized_words = recognized_text.lower().split()
    target_words = target_text.lower().split()
    target_copy = list(target_words)
    matches = 0
    for word in recognized_words:
        if word in target_copy:
            matches += 1
            target_copy.remove(word)
    denominator = max(len(recognized_words), len(target_words))
    return matches / denominator if denominator else 0.0


def _scores_from_component(test_data, component_key):
    scores = []
    if component_key not in test_data:
        return scores
    comp = test_data[component_key]
    if isinstance(comp, dict) and 'input' in comp and 'target' in comp:
        scores.append(calculate_accuracy(comp['input'], comp['target']))
        return scores
    if isinstance(comp, dict):
        for test in comp.values():
            if isinstance(test, dict) and 'input' in test and 'target' in test:
                scores.append(calculate_accuracy(test['input'], test['target']))
    return scores


def extract_test_features(test_data):
    features = {}
    confidence_scores = {}

    reading_accuracy = _scores_from_component(test_data, 'reading')
    if reading_accuracy:
        features['reading_accuracy_1'] = float(np.mean(reading_accuracy))
        features['reading_accuracy_2'] = float(
            reading_accuracy[1] if len(reading_accuracy) > 1 else reading_accuracy[0]
        )
        confidence_scores['reading'] = {
            'mean_accuracy': float(np.mean(reading_accuracy)),
            'scores': reading_accuracy,
        }

    spelling_accuracy = _scores_from_component(test_data, 'spelling')
    if spelling_accuracy:
        features['spelling_accuracy_1'] = float(np.mean(spelling_accuracy))
        features['spelling_accuracy_2'] = float(
            spelling_accuracy[1] if len(spelling_accuracy) > 1 else spelling_accuracy[0]
        )
        confidence_scores['spelling'] = {
            'mean_accuracy': float(np.mean(spelling_accuracy)),
            'scores': spelling_accuracy,
        }

    letter_accuracy = _scores_from_component(test_data, 'letter_recognition')
    if letter_accuracy:
        features['letter_accuracy_1'] = float(np.mean(letter_accuracy))
        features['letter_accuracy_2'] = float(
            letter_accuracy[1] if len(letter_accuracy) > 1 else letter_accuracy[0]
        )
        confidence_scores['letter_recognition'] = {
            'mean_accuracy': float(np.mean(letter_accuracy)),
            'scores': letter_accuracy,
        }

    for key, feat_name in (
        ('word_matching', 'word_matching_accuracy'),
        ('number_reading', 'number_reading_accuracy'),
        ('sentence_copying', 'sentence_copying_accuracy'),
    ):
        scores = _scores_from_component(test_data, key)
        if scores:
            acc = float(scores[0])
            features[feat_name] = acc
            confidence_scores[key] = {'accuracy': acc}

    if 'handwriting_features' in test_data:
        hw = test_data['handwriting_features']
        for k, v in hw.items():
            features[k] = float(v)
        hw_scores = list(hw.values())
        if hw_scores:
            confidence_scores['handwriting'] = {
                'mean_score': float(np.mean(hw_scores)),
                'features': hw,
            }

    return features, confidence_scores


def calculate_overall_confidence(confidence_scores):
    weights = {
        'reading': 0.25,
        'spelling': 0.20,
        'letter_recognition': 0.15,
        'word_matching': 0.10,
        'number_reading': 0.10,
        'sentence_copying': 0.10,
        'handwriting': 0.10,
    }
    total_weight = 0.0
    weighted_sum = 0.0
    for component, weight in weights.items():
        if component not in confidence_scores:
            continue
        score_dict = confidence_scores[component]
        if 'mean_accuracy' in score_dict:
            score = score_dict['mean_accuracy']
        elif 'mean_score' in score_dict:
            score = score_dict['mean_score']
        elif 'accuracy' in score_dict:
            score = score_dict['accuracy']
        else:
            continue
        weighted_sum += score * weight
        total_weight += weight

    overall_score = weighted_sum / total_weight if total_weight > 0 else 0.5

    if overall_score >= 0.85:
        risk_level = 0
    elif overall_score >= 0.75:
        risk_level = 1
    elif overall_score >= 0.60:
        risk_level = 2
    else:
        risk_level = 3

    return {
        'score': overall_score,
        'risk_level': risk_level,
        'confidence': overall_score * 100,
    }


def build_feature_vector(features):
    return np.array([[features.get(name, 0.5) for name in FEATURE_ORDER]], dtype=np.float64)


def predict_dyslexia_risk(features, model_path):
    bundle = get_dyslexia_bundle(model_path)
    if bundle is None:
        return None, None, None

    vec = build_feature_vector(features)
    scaled = bundle['scaler'].transform(vec)
    clf = bundle['model']
    pred_class = int(clf.predict(scaled)[0])
    proba = clf.predict_proba(scaled)[0].tolist()

    risk_level = ML_CLASS_TO_APP_RISK.get(pred_class, 2)
    return risk_level, proba, pred_class


def merge_ml_and_heuristic(ml_risk, overall_result):
    """Combine ML class with heuristic score; excellent tier from high performance."""
    score = overall_result['score']
    heuristic_risk = overall_result['risk_level']
    if score >= 0.85:
        return 0, score
    if ml_risk is not None:
        combined = max(ml_risk, heuristic_risk) if score < 0.75 else min(ml_risk, heuristic_risk)
        return combined, score
    return heuristic_risk, score


def get_feature_importance(features, model_path):
    bundle = get_dyslexia_bundle(model_path)
    if bundle is None:
        return {}
    clf = bundle['model']
    if not hasattr(clf, 'feature_importances_'):
        return {}
    importance = {}
    if hasattr(clf, 'feature_names_in_'):
        for i, name in enumerate(clf.feature_names_in_):
            if name in features:
                importance[name] = float(clf.feature_importances_[i])
    else:
        for i, name in enumerate(FEATURE_ORDER):
            if i < len(clf.feature_importances_):
                importance[name] = float(clf.feature_importances_[i])
    return importance


def generate_recommendations(component_scores, overall_score, risk_level):
    recommendations = []
    if risk_level == 0:
        recommendations.append(
            'Overall performance is excellent with strong reading and processing skills.'
        )
    elif risk_level == 1:
        recommendations.append(
            'Overall performance shows some minor areas for improvement, but generally good skills.'
        )
    elif risk_level == 2:
        recommendations.append(
            'Some indicators of potential reading difficulties were detected. '
            'Consider consulting with an education specialist for further assessment.'
        )
    else:
        recommendations.append(
            'Several indicators of potential dyslexia were detected. '
            'We recommend consulting with a dyslexia specialist for a comprehensive evaluation.'
        )

    tips = {
        'reading': (
            'Reading: Consider daily reading practice with gradually increasing difficulty.',
            'Reading: Continue regular reading practice to build fluency.',
        ),
        'spelling': (
            'Spelling: Practice multisensory spelling techniques.',
            'Spelling: Continue building spelling skills through word games.',
        ),
        'handwriting': (
            'Handwriting: Regular fine motor exercises and handwriting practice.',
            'Handwriting: Continue practicing consistent letter formation.',
        ),
    }
    for comp, (low, mid) in tips.items():
        if comp in component_scores:
            s = component_scores[comp]
            if s < 0.7:
                recommendations.append(low)
            elif s < 0.85:
                recommendations.append(mid)

    if overall_score < 0.7:
        recommendations.append(
            'Technology: Consider text-to-speech and speech-to-text tools to support reading and writing.'
        )
    return recommendations


def save_test_results(test_data, features, risk_level, confidence_scores, overall_result,
                      user_id=None, component_scores=None, recommendations=None,
                      feature_importance=None):
    try:
        if user_id:
            from app.services.progress_service import save_screening_result
            cs = component_scores or {}
            if not cs:
                for test_type, scores in (confidence_scores or {}).items():
                    if 'mean_accuracy' in scores:
                        cs[test_type] = scores['mean_accuracy']
                    elif 'mean_score' in scores:
                        cs[test_type] = scores['mean_score']
                    elif 'accuracy' in scores:
                        cs[test_type] = scores['accuracy']
            recs = recommendations or generate_recommendations(
                cs, overall_result.get('score', 0.5), risk_level
            )
            save_screening_result(
                user_id,
                overall_result.get('score', 0.5),
                risk_level,
                cs,
                recs,
                feature_importance or {},
            )
        results_dir = os.path.join(os.getcwd(), 'test_results')
        os.makedirs(results_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filepath = os.path.join(results_dir, f'test_result_{timestamp}.json')
        result_data = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'risk_level': int(risk_level),
            'overall_result': overall_result,
            'confidence_scores': confidence_scores,
            'features': features,
            'test_metadata': {
                'components': list(test_data.keys()),
                'has_handwriting': 'handwriting_features' in test_data,
            },
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, indent=2)
        return True
    except Exception as e:
        logger.error('Error saving test results: %s', e)
        return False


def submit_simple(test_data, user_id=None):
    if not test_data:
        return {'success': False, 'error': 'No test data provided'}, 400

    component_scores = {}
    for component in (
        'reading', 'spelling', 'letter_recognition',
        'word_matching', 'number_reading', 'sentence_copying',
    ):
        if component not in test_data:
            continue
        values = []
        comp = test_data[component]
        if isinstance(comp, dict) and 'input' in comp:
            inp_len = len(str(comp['input']))
            tgt_len = len(str(comp['target']))
            if inp_len and tgt_len:
                values.append(min(inp_len, tgt_len) / max(inp_len, tgt_len))
        else:
            for test in comp.values():
                if isinstance(test, dict) and 'input' in test and 'target' in test:
                    inp_len = len(str(test['input']))
                    tgt_len = len(str(test['target']))
                    if inp_len and tgt_len:
                        values.append(min(inp_len, tgt_len) / max(inp_len, tgt_len))
        if values:
            component_scores[component] = sum(values) / len(values)

    if 'handwriting_features' in test_data:
        hw = list(test_data['handwriting_features'].values())
        if hw:
            component_scores['handwriting'] = sum(hw) / len(hw)

    overall_score = (
        sum(component_scores.values()) / len(component_scores)
        if component_scores else 0.5
    )
    if overall_score >= 0.80:
        risk_level = 0
    elif overall_score >= 0.70:
        risk_level = 1
    elif overall_score >= 0.60:
        risk_level = 2
    else:
        risk_level = 3

    recommendations = generate_recommendations(
        component_scores, overall_score, risk_level
    )
    if user_id:
        save_test_results(
            test_data, {}, risk_level, {}, {'score': overall_score, 'risk_level': risk_level},
            user_id=user_id, component_scores=component_scores, recommendations=recommendations,
        )
    return {
        'success': True,
        'result': {
            'prediction': risk_level,
            'overall_score': overall_score,
            'component_scores': component_scores,
            'recommendations': recommendations,
        },
    }, 200


def submit_full(test_data, model_path, user_id=None):
    if not test_data:
        return {'success': False, 'error': 'No test data provided'}, 400

    features, confidence_scores = extract_test_features(test_data)
    overall_result = calculate_overall_confidence(confidence_scores)

    component_scores = {}
    for test_type, scores in confidence_scores.items():
        if 'mean_accuracy' in scores:
            component_scores[test_type] = scores['mean_accuracy']
        elif 'mean_score' in scores:
            component_scores[test_type] = scores['mean_score']
        elif 'accuracy' in scores:
            component_scores[test_type] = scores['accuracy']

    ml_risk, proba, ml_class = predict_dyslexia_risk(features, model_path)
    risk_level, overall_score = merge_ml_and_heuristic(ml_risk, overall_result)
    overall_result['risk_level'] = risk_level
    overall_result['score'] = overall_score

    feature_importance = get_feature_importance(features, model_path)
    recommendations = generate_recommendations(
        component_scores, overall_score, risk_level
    )
    save_test_results(
        test_data, features, risk_level, confidence_scores, overall_result,
        user_id=user_id, component_scores=component_scores,
        recommendations=recommendations, feature_importance=feature_importance,
    )

    return {
        'success': True,
        'result': {
            'prediction': risk_level,
            'overall_score': overall_score,
            'component_scores': component_scores,
            'feature_importance': feature_importance,
            'confidence_scores': confidence_scores,
            'overall_confidence': overall_result,
            'ml_class': ml_class,
            'ml_probabilities': proba,
            'recommendations': recommendations,
        },
    }, 200
