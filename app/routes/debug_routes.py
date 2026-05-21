"""Debug-only routes; disabled unless ENABLE_DEBUG_ROUTES=1."""

import logging
from datetime import datetime

from flask import Blueprint, current_app, jsonify, redirect, session

from app.services.dyslexia_service import generate_recommendations

logger = logging.getLogger(__name__)

debug_bp = Blueprint('debug', __name__)


def _debug_guard():
    if not current_app.config.get('ENABLE_DEBUG_ROUTES'):
        return jsonify({'success': False, 'error': 'Not found'}), 404
    return None


@debug_bp.route('/guaranteed_test_result', methods=['POST', 'GET'])
def guaranteed_test_result():
    blocked = _debug_guard()
    if blocked:
        return blocked
    component_scores = {
        'reading': 0.95, 'spelling': 0.92, 'letter_recognition': 0.98,
        'word_matching': 0.90, 'number_reading': 0.88,
        'sentence_copying': 0.94, 'handwriting': 0.85,
    }
    handwriting_features = session.get('test_data', {}).get('handwriting_features', {})
    return jsonify({
        'success': True,
        'result': {
            'prediction': 0,
            'overall_score': 0.92,
            'component_scores': component_scores,
            'handwriting_features': handwriting_features,
            'recommendations': generate_recommendations(component_scores, 0.92, 0),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'demo': True,
        },
    })


@debug_bp.route('/check_session', methods=['GET'])
def check_session():
    blocked = _debug_guard()
    if blocked:
        return blocked
    session_data = {}
    if 'test_data' in session:
        session_data['test_data'] = session['test_data']
    if 'reading_results' in session:
        session_data['reading_results'] = session['reading_results']
    return jsonify({'success': True, 'session_data': session_data})


@debug_bp.route('/test_data_sample', methods=['GET'])
def test_data_sample():
    blocked = _debug_guard()
    if blocked:
        return blocked
    return jsonify({
        'reading': {'test1': {'input': 'a', 'target': 'a'}},
        'spelling': {'test1': {'input': 'cat', 'target': 'cat'}},
    })


@debug_bp.route('/get_fixed_test_data', methods=['GET'])
@debug_bp.route('/guaranteed_test_result_with_lime_shap', methods=['GET'])
def fixed_test_data():
    blocked = _debug_guard()
    if blocked:
        return blocked
    return jsonify({
        'success': True,
        'result': {
            'prediction': 0,
            'overall_score': 0.92,
            'demo': True,
            'lime_explanation': {'reading_accuracy_1 > 0.75': 0.01},
            'shap_explanation': {'reading_accuracy_1': 0.01},
        },
    })


@debug_bp.route('/fixed_test_results_with_lime', methods=['GET'])
def fixed_test_results_with_lime():
    blocked = _debug_guard()
    if blocked:
        return blocked
    return redirect('/dyslexia_screening?show_fixed_results=true')
