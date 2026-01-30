# Skin Tone Classifier API
FROM python:3.11-slim-bookworm

WORKDIR /app

# System deps for OpenCV headless (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy and install deps: use headless OpenCV (smaller, no GUI)
COPY requirements.txt ./
RUN grep -v '^opencv-python' requirements.txt > /tmp/req.txt \
    && echo 'opencv-python-headless~=4.10.0.84' >> /tmp/req.txt \
    && pip install --no-cache-dir -r /tmp/req.txt \
    && find /usr/local/lib -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

COPY src/ ./src/
COPY main.py ./

ENV PYTHONPATH=/app/src
ENV PORT=8000
EXPOSE 8000

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
