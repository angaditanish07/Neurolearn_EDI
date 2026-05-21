import io
import logging

from flask import Blueprint, current_app, jsonify, request, session

from app.routes.auth import login_required
from app.services import dyslexia_service
from app.services.handwriting_service import analyze_handwriting
from app.services.progress_service import parent_owns_child, record_progress_event

logger = logging.getLogger(__name__)

dyslexia_bp = Blueprint('dyslexia', __name__)


def _merge_handwriting(test_data):
    if 'test_data' in session and 'handwriting_features' in session.get('test_data', {}):
        test_data['handwriting_features'] = session['test_data']['handwriting_features']
    return test_data


@dyslexia_bp.route('/analyze_handwriting', methods=['POST'])
@login_required
def analyze_handwriting_endpoint():
    try:
        if 'handwriting_image' not in request.files:
            return jsonify({'success': False, 'error': 'No image file provided'}), 400
        image_data = request.files['handwriting_image'].read()
        features = analyze_handwriting(image_data)
        if not features:
            return jsonify({'success': False, 'error': 'Failed to analyze handwriting'}), 400

        if 'test_data' not in session:
            session['test_data'] = {}
        session['test_data']['handwriting_features'] = features
        session.modified = True

        return jsonify({'success': True, 'features': features})
    except Exception as e:
        logger.error('analyze_handwriting: %s', e)
        if current_app.debug:
            return jsonify({'success': False, 'error': str(e)}), 500
        return jsonify({'success': False, 'error': 'Handwriting analysis failed'}), 500


@dyslexia_bp.route('/submit_dyslexia_test_simple', methods=['POST'])
@login_required
def submit_dyslexia_test_simple():
    try:
        test_data = request.get_json()
        if not test_data:
            return jsonify({'success': False, 'error': 'No test data provided'}), 400
        test_data = _merge_handwriting(test_data)
        body, code = dyslexia_service.submit_simple(test_data, user_id=session['user_id'])
        return jsonify(body), code
    except Exception as e:
        logger.error('submit_dyslexia_test_simple: %s', e)
        if current_app.debug:
            return jsonify({'success': False, 'error': str(e)}), 500
        return jsonify({'success': False, 'error': 'Submission failed'}), 500


@dyslexia_bp.route('/submit_dyslexia_test', methods=['POST'])
@login_required
def submit_dyslexia_test():
    try:
        test_data = request.get_json()
        if not test_data:
            return jsonify({'success': False, 'error': 'No test data provided'}), 400
        test_data = _merge_handwriting(test_data)
        body, code = dyslexia_service.submit_full(
            test_data, current_app.config['DYSLEXIA_MODEL_PATH'],
            user_id=session['user_id'],
        )
        return jsonify(body), code
    except Exception as e:
        logger.error('submit_dyslexia_test: %s', e)
        if current_app.debug:
            return jsonify({'success': False, 'error': str(e)}), 500
        return jsonify({'success': False, 'error': 'Submission failed'}), 500


@dyslexia_bp.route('/analyze_reading', methods=['POST'])
@login_required
def analyze_reading():
    try:
        import speech_recognition as sr
        from pydub import AudioSegment
    except ImportError:
        return jsonify({
            'success': False,
            'error': 'Speech recognition dependencies not installed',
        }), 503

    try:
        if 'audio' not in request.files:
            return jsonify({'success': False, 'error': 'No audio file provided'}), 400

        audio_file = request.files['audio']
        test_id = request.form.get('test_id')
        target_text = request.form.get('target_text', '')

        audio_segment = AudioSegment.from_file(io.BytesIO(audio_file.read()))
        audio_segment = audio_segment.set_frame_rate(16000).set_channels(1)

        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 300
        recognizer.dynamic_energy_threshold = True

        wav_data = io.BytesIO()
        audio_segment.export(wav_data, format='wav')
        wav_data.seek(0)

        with sr.AudioFile(wav_data) as source:
            audio = recognizer.record(source)
            recognized_text = recognizer.recognize_google(audio, language='en-US')

        accuracy = dyslexia_service.calculate_accuracy(recognized_text, target_text)
        if 'reading_results' not in session:
            session['reading_results'] = {}
        session['reading_results'][test_id] = {
            'accuracy': accuracy,
            'recognized_text': recognized_text,
        }
        session.modified = True

        return jsonify({
            'success': True,
            'accuracy': accuracy,
            'recognized_text': recognized_text,
        })
    except Exception as e:
        logger.error('analyze_reading: %s', e)
        err_name = type(e).__name__
        if err_name == 'UnknownValueError':
            return jsonify({
                'success': False,
                'error': 'Could not understand audio. Please speak clearly and try again.',
            }), 200
        if current_app.debug:
            return jsonify({'success': False, 'error': str(e)}), 500
        return jsonify({'success': False, 'error': 'Reading analysis failed'}), 500


@dyslexia_bp.route('/get_reading_results', methods=['GET'])
@login_required
def get_reading_results():
    return jsonify({
        'success': True,
        'results': session.get('reading_results', {}),
    })


@dyslexia_bp.route('/notify_parent', methods=['POST'])
@login_required
def notify_parent():
    try:
        data = request.get_json() or {}
        if data.get('action') != 'video_call_request':
            return jsonify({'success': False, 'error': 'Invalid action'}), 400

        child_id = data.get('child_id') or session.get('user_id')
        if session.get('role') == 'parent' and data.get('child_id'):
            if not parent_owns_child(session['user_id'], int(child_id)):
                return jsonify({'success': False, 'error': 'Not linked to this child'}), 403

        from datetime import datetime
        from app.extensions import socketio
        socketio.emit('video_call_request', {
            'timestamp': datetime.now().isoformat(),
            'child_id': child_id,
            'requested_by': session.get('user_id'),
        })

        return jsonify({'success': True, 'message': 'Parent notification sent'})
    except Exception as e:
        logger.error('notify_parent: %s', e)
        if current_app.debug:
            return jsonify({'success': False, 'error': str(e)}), 500
        return jsonify({'success': False, 'error': 'Notification failed'}), 500
