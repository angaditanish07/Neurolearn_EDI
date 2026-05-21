import logging
import joblib
import cv2

logger = logging.getLogger(__name__)

_emotion_model = None
_dyslexia_bundle = None
_face_mesh = None
_face_classifier = None
_hands_detector = None


def get_emotion_model(path):
    global _emotion_model
    if _emotion_model is None:
        from tensorflow.keras.models import load_model
        logger.info('Loading emotion detection model from %s', path)
        _emotion_model = load_model(path, compile=False)
        logger.info('Emotion model loaded')
    return _emotion_model


def get_dyslexia_bundle(path):
    global _dyslexia_bundle
    if _dyslexia_bundle is None:
        try:
            bundle = joblib.load(path)
            if isinstance(bundle, dict) and 'model' in bundle and 'scaler' in bundle:
                _dyslexia_bundle = bundle
                logger.info('Dyslexia model bundle loaded')
            else:
                logger.error('Invalid dyslexia model format')
        except Exception as e:
            logger.error('Error loading dyslexia model: %s', e)
    return _dyslexia_bundle


def get_face_mesh():
    global _face_mesh
    if _face_mesh is None:
        try:
            import mediapipe as mp
            _face_mesh = mp.solutions.face_mesh.FaceMesh(
                static_image_mode=False,
                max_num_faces=1,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5,
            )
        except Exception as e:
            logger.error('MediaPipe FaceMesh init failed: %s', e)
    return _face_mesh


def get_hands_detector():
    global _hands_detector
    if _hands_detector is None:
        try:
            import mediapipe as mp
            _hands_detector = mp.solutions.hands.Hands(
                static_image_mode=True,
                max_num_hands=2,
                min_detection_confidence=0.4,
                min_tracking_confidence=0.4,
            )
        except Exception as e:
            logger.error('MediaPipe Hands init failed: %s', e)
    return _hands_detector


def get_face_classifier():
    global _face_classifier
    if _face_classifier is None:
        _face_classifier = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
    return _face_classifier


def models_health():
    return {
        'emotion_loaded': _emotion_model is not None,
        'dyslexia_loaded': _dyslexia_bundle is not None,
        'face_mesh_loaded': _face_mesh is not None,
        'hands_loaded': _hands_detector is not None,
    }
