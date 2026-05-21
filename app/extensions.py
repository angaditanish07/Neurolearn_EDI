import sys

from flask_socketio import SocketIO

# eventlet is unreliable on Windows; threading works without Docker
_ASYNC_MODE = 'threading' if sys.platform == 'win32' else 'eventlet'

socketio = SocketIO(async_mode=_ASYNC_MODE)
active_connections = {}
