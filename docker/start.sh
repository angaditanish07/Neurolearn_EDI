#!/bin/sh
# Render sets PORT dynamically — must not hardcode 8080
set -e
PORT="${PORT:-8080}"
echo "Starting gunicorn on 0.0.0.0:${PORT}"
exec gunicorn \
  -k eventlet \
  -w 1 \
  --timeout 120 \
  --graceful-timeout 30 \
  -b "0.0.0.0:${PORT}" \
  wsgi:app
