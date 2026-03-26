#!/bin/sh
set -eu

mkdir -p /app/data /app/uploads "${MUSIC_AGENT_DOWNLOAD_DIR}"

alembic upgrade head
python scripts/seed_db.py

exec python app.py
