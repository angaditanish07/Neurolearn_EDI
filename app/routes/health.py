from flask import Blueprint, current_app, jsonify

from app.ml.loaders import models_health
from app.utils.audio_utils import ffmpeg_available

health_bp = Blueprint('health', __name__)


@health_bp.route('/healthz')
def healthz():
    return jsonify({
        'status': 'ok',
        'models': models_health(),
        'ffmpeg': ffmpeg_available(),
        'audio_note': (
            'WAV recordings work without ffmpeg; WebM/MP4 need ffmpeg on server '
            'unless the browser converts to WAV first.'
        ),
        'debug_routes': current_app.config.get('ENABLE_DEBUG_ROUTES', False),
    })
