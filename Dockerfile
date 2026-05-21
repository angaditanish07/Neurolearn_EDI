FROM python:3.11-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    ffmpeg \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/
COPY templates/ templates/
COPY static/ static/
COPY wsgi.py .
COPY docker/start.sh /start.sh
RUN chmod +x /start.sh
COPY fer2013_mini_XCEPTION.102-0.66.hdf5 dyslexia_model.joblib ./

ENV FLASK_ENV=production
ENV FLASK_DEBUG=0
ENV HOST=0.0.0.0

# Render injects PORT at runtime — do not hardcode in CMD
CMD ["/start.sh"]
