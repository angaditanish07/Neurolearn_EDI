from flask import Blueprint, current_app, jsonify

from app.ml.loaders import models_health
from app.mongo import get_client
from app.utils.audio_utils import ffmpeg_available

health_bp = Blueprint('health', __name__)


def _mongodb_ok():
    try:
        get_client().admin.command('ping')
        return True
    except Exception:
        return False


@health_bp.route('/healthz')
def healthz():
    return jsonify({
        'status': 'ok',
        'mongodb': _mongodb_ok(),
        'database': current_app.config.get('MONGODB_DB_NAME'),
        'models': models_health(),
        'ffmpeg': ffmpeg_available(),
        'audio_note': (
            'WAV recordings work without ffmpeg; WebM/MP4 need ffmpeg on server '
            'unless the browser converts to WAV first.'
        ),
        'debug_routes': current_app.config.get('ENABLE_DEBUG_ROUTES', False),
    })
