"""WSGI entry for gunicorn: gunicorn -k eventlet -w 1 'wsgi:app'"""
from app import create_app
from app.extensions import socketio

flask_app = create_app()
app = flask_app
