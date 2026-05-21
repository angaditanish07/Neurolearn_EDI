"""WSGI entry for gunicorn: gunicorn -k eventlet -w 1 'wsgi:app'"""
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s: %(message)s',
    stream=sys.stderr,
)

try:
    from app import create_app

    app = create_app()
    logging.getLogger(__name__).info('NeuroLearn application created successfully')
except Exception:
    logging.getLogger(__name__).exception('Failed to create NeuroLearn application')
    raise
