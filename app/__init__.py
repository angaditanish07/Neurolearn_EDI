import logging
import os

from flask import Flask

from app.config import Config
from app.extensions import socketio

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Project root (parent of app/ package) — templates & static live here
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def create_app(config_class=Config):
    flask_app = Flask(
        __name__,
        template_folder=os.path.join(PROJECT_ROOT, 'templates'),
        static_folder=os.path.join(PROJECT_ROOT, 'static'),
        static_url_path='/static',
    )
    flask_app.config.from_object(config_class)

    os.chdir(PROJECT_ROOT)

    uploads = flask_app.config['UPLOAD_FOLDER']
    if not os.path.isabs(uploads):
        uploads = os.path.join(PROJECT_ROOT, uploads)
        flask_app.config['UPLOAD_FOLDER'] = uploads
    os.makedirs(uploads, exist_ok=True)
    os.makedirs(os.path.join(PROJECT_ROOT, 'test_results'), exist_ok=True)

    for key in ('EMOTION_MODEL_PATH', 'DYSLEXIA_MODEL_PATH'):
        path = flask_app.config[key]
        if path and not os.path.isabs(path):
            flask_app.config[key] = os.path.join(PROJECT_ROOT, path)

    log_level = logging.DEBUG if flask_app.config['DEBUG'] else logging.INFO
    logging.basicConfig(level=log_level)
    logger = logging.getLogger(__name__)

    if not os.environ.get('FLASK_SECRET_KEY'):
        logger.warning(
            'FLASK_SECRET_KEY not set; using generated key (sessions reset on restart)'
        )

    _configure_sessions(flask_app)

    from app.db import init_db
    init_db(flask_app)

    socketio.init_app(flask_app, cors_allowed_origins='*')

    from app.routes.pages import pages_bp
    from app.routes.emotion import emotion_bp
    from app.routes.dyslexia import dyslexia_bp
    from app.routes.health import health_bp
    from app.routes.auth import auth_bp
    from app.routes.progress import progress_bp
    from app.routes.parent import parent_bp
    from app.routes.debug_routes import debug_bp
    import app.routes.websocket  # noqa: F401 — register socket handlers

    flask_app.register_blueprint(pages_bp)
    flask_app.register_blueprint(emotion_bp)
    flask_app.register_blueprint(dyslexia_bp)
    flask_app.register_blueprint(health_bp)
    flask_app.register_blueprint(auth_bp)
    flask_app.register_blueprint(progress_bp)
    flask_app.register_blueprint(parent_bp)
    flask_app.register_blueprint(debug_bp)

    return flask_app


def _configure_sessions(flask_app):
    redis_url = flask_app.config.get('REDIS_URL')
    if redis_url:
        try:
            from flask_session import Session
            flask_app.config['SESSION_TYPE'] = 'redis'
            import redis
            flask_app.config['SESSION_REDIS'] = redis.from_url(redis_url)
            Session(flask_app)
        except ImportError:
            logging.getLogger(__name__).warning(
                'flask-session/redis not installed; using cookie sessions'
            )
