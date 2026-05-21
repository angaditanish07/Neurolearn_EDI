import logging

from flask import request
from flask_socketio import emit

from app.extensions import socketio

logger = logging.getLogger(__name__)


@socketio.on('connect')
def handle_connect():
    from app.extensions import active_connections
    active_connections[request.sid] = True
    logger.info('Client connected: %s', request.sid)


@socketio.on('disconnect')
def handle_disconnect():
    from app.extensions import active_connections
    active_connections.pop(request.sid, None)
    logger.info('Client disconnected: %s', request.sid)


@socketio.on('webrtc_signal')
def handle_webrtc_signal(data):
    from app.extensions import active_connections
    try:
        target_sid = (data or {}).get('target')
        if target_sid and target_sid in active_connections:
            emit('webrtc_signal', data, room=target_sid)
    except Exception as e:
        logger.error('WebRTC signal error: %s', e)
