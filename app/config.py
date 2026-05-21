import os
import secrets

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Config:
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or secrets.token_hex(32)
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
    EMOTION_MODEL_PATH = os.environ.get(
        'EMOTION_MODEL_PATH', 'fer2013_mini_XCEPTION.102-0.66.hdf5'
    )
    DYSLEXIA_MODEL_PATH = os.environ.get('DYSLEXIA_MODEL_PATH', 'dyslexia_model.joblib')
    ENABLE_DEBUG_ROUTES = os.environ.get('ENABLE_DEBUG_ROUTES', '0') == '1'
    DEBUG = os.environ.get('FLASK_DEBUG', '0') == '1'
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', '0') == '1'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax')
    REDIS_URL = (os.environ.get('REDIS_URL') or '').strip()
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', '8080'))
    MONGODB_URI = (os.environ.get('MONGODB_URI') or 'mongodb://localhost:27017/').strip()
    MONGODB_DB_NAME = (os.environ.get('MONGODB_DB_NAME') or 'neurolearn').strip()
    USE_HTTPS = os.environ.get('USE_HTTPS', '0').strip() in ('1', 'true', 'yes')


def is_production():
    return os.environ.get('FLASK_ENV', 'development') == 'production'
