import logging

from flask import Blueprint, current_app, jsonify, request, session

from app.routes.auth import login_required
from app.services.emotion_service import detect_emotion_from_image
from app.services.face_service import extract_face_landmarks
from app.services.finger_service import count_fingers_in_image
from app.services.progress_service import record_progress_event
from app.utils.image_utils import process_base64_image

logger = logging.getLogger(__name__)

emotion_bp = Blueprint('emotion', __name__)


@emotion_bp.route('/detect_emotion', methods=['POST'])
@login_required
def detect_emotion():
    try:
        if 'image' not in request.form:
            return jsonify({'error': 'No image data provided'}), 400
        img = process_base64_image(request.form['image'])
        result, err = detect_emotion_from_image(
            img, current_app.config['EMOTION_MODEL_PATH']
        )
        if err:
            return jsonify({'error': err}), 200
        if result:
            record_progress_event(session['user_id'], 'interactive_emotion', {
                'emotion': result.get('emotion'),
            })
        return jsonify(result)
    except Exception as e:
        logger.error('detect_emotion: %s', e)
        if current_app.debug:
            return jsonify({'error': str(e)}), 500
        return jsonify({'error': 'Emotion detection failed'}), 500


@emotion_bp.route('/start_face_features', methods=['POST'])
@login_required
def start_face_features():
    try:
        if 'image' not in request.form:
            return jsonify({'success': False, 'error': 'No image data provided'}), 400
        img = process_base64_image(request.form['image'])
        result, err = extract_face_landmarks(img)
        if err:
            return jsonify({'success': False, 'error': err}), 200
        return jsonify(result)
    except Exception as e:
        logger.error('start_face_features: %s', e)
        if current_app.debug:
            return jsonify({'success': False, 'error': str(e)}), 500
        return jsonify({'success': False, 'error': 'Face feature detection failed'}), 500


@emotion_bp.route('/count_fingers', methods=['POST'])
@login_required
def count_fingers():
    try:
        if 'image' not in request.form:
            return jsonify({'success': False, 'error': 'No image data provided'}), 400
        img = process_base64_image(request.form['image'])
        result, err = count_fingers_in_image(img)
        if err:
            return jsonify({'success': False, 'error': err}), 503
        if result and result.get('success'):
            record_progress_event(session['user_id'], 'interactive_fingers', {
                'total_fingers': result.get('total_fingers'),
            })
        return jsonify(result)
    except Exception as e:
        logger.error('count_fingers: %s', e)
        if current_app.debug:
            return jsonify({'success': False, 'error': str(e)}), 500
        return jsonify({'success': False, 'error': 'Finger counting failed'}), 500
