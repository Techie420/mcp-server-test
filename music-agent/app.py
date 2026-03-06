from __future__ import annotations

import logging
from pathlib import Path
from uuid import uuid4

from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

from config import Settings
from downloader import download_preview_as_mp3, is_already_downloaded, target_mp3_path
from search import search_song_preview
from utils import ensure_directory, retry, setup_logging
from vision import detect_song_and_artist, extract_text_from_image

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".webp"}


def _is_allowed_image(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def process_image(image_path: Path, settings: Settings) -> dict[str, str]:
    extract = retry(settings.max_retries, settings.retry_backoff_seconds)(extract_text_from_image)
    search = retry(settings.max_retries, settings.retry_backoff_seconds)(search_song_preview)
    download = retry(settings.max_retries, settings.retry_backoff_seconds)(download_preview_as_mp3)

    extracted_text = extract(image_path, settings.tesseract_psm)
    guess = detect_song_and_artist(extracted_text)
    result = search(guess.title, guess.artist, settings.user_agent)
    out_path = target_mp3_path(settings.base_download_dir, result.artist, result.title)

    if is_already_downloaded(out_path):
        return {
            "artist": result.artist,
            "title": result.title,
            "source_url": result.source_url,
            "saved_path": str(out_path),
            "status": "Skipped (already downloaded)",
            "confidence": guess.confidence_note,
        }

    saved = download(result.preview_url, out_path)
    return {
        "artist": result.artist,
        "title": result.title,
        "source_url": result.source_url,
        "saved_path": str(saved),
        "status": "Downloaded",
        "confidence": guess.confidence_note,
    }


def create_app() -> Flask:
    settings = Settings.from_env()
    setup_logging(settings.log_level)

    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 15 * 1024 * 1024

    upload_dir = Path("uploads")
    ensure_directory(upload_dir)

    @app.route("/", methods=["GET", "POST"])
    def index():
        error: str | None = None
        result: dict[str, str] | None = None

        if request.method == "POST":
            file = request.files.get("screenshot")
            if file is None or not file.filename:
                error = "Select an image file first."
            elif not _is_allowed_image(file.filename):
                error = "Unsupported file type. Use png, jpg, jpeg, bmp, or webp."
            else:
                safe_name = secure_filename(file.filename)
                file_path = upload_dir / f"{uuid4().hex}_{safe_name}"
                file.save(file_path)
                try:
                    result = process_image(file_path, settings)
                except Exception as exc:  # noqa: BLE001
                    logger.exception("Processing failed")
                    error = str(exc)
                finally:
                    if file_path.exists():
                        file_path.unlink()

        return render_template("index.html", error=error, result=result)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
