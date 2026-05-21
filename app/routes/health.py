from flask import Blueprint, current_app, jsonify

from app.ml.loaders import models_health

health_bp = Blueprint('health', __name__)


@health_bp.route('/healthz')
def healthz():
    return jsonify({
        'status': 'ok',
        'models': models_health(),
        'debug_routes': current_app.config.get('ENABLE_DEBUG_ROUTES', False),
    })
