FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=5000 \
    MUSIC_AGENT_HOST=0.0.0.0 \
    DATABASE_URL=sqlite:////app/data/music_agent.db \
    MUSIC_AGENT_DOWNLOAD_DIR=/app/data/downloads/music

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ffmpeg \
        tesseract-ocr \
        libgl1 \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . .

RUN mkdir -p /app/data /app/uploads /app/downloads/music \
    && chmod +x /app/entrypoint.sh

EXPOSE 5000

VOLUME ["/app/data"]

ENTRYPOINT ["/app/entrypoint.sh"]
