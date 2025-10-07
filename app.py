from __future__ import annotations

import os
from pathlib import Path
from uuid import uuid4

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from werkzeug.utils import secure_filename

from upscaler import upscale_image_file

BASE_DIR = Path(__file__).parent
UPLOAD_FOLDER = BASE_DIR / "uploads"
RESULT_FOLDER = BASE_DIR / "generated"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "bmp", "tiff"}

UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
RESULT_FOLDER.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
app.config["RESULT_FOLDER"] = str(RESULT_FOLDER)
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024  # 25 MB upload limit
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


@app.post("/upload")
def upload_file():
    if "image" not in request.files:
        flash("No file part in the request.")
        return redirect(url_for("index"))

    file = request.files["image"]

    if file.filename == "":
        flash("No file selected.")
        return redirect(url_for("index"))

    if not allowed_file(file.filename):
        flash("Unsupported file type. Please upload an image file.")
        return redirect(url_for("index"))

    original_filename = secure_filename(file.filename)
    upload_name = f"{uuid4().hex}_{original_filename}"
    upload_path = UPLOAD_FOLDER / upload_name
    file.save(upload_path)

    result_name = f"{uuid4().hex}_4k.png"
    result_path = RESULT_FOLDER / result_name

    try:
        upscale_image_file(upload_path, result_path)
    except Exception as exc:  # pragma: no cover - defensive error surface
        flash("Failed to upscale the image. Please try another file.")
        app.logger.exception("Error while upscaling image: %s", exc)
        if upload_path.exists():
            upload_path.unlink(missing_ok=True)
        return redirect(url_for("index"))

    download_url = url_for("download_file", filename=result_name)
    return render_template(
        "index.html",
        download_url=download_url,
        original_filename=original_filename,
    )


@app.route("/download/<path:filename>")
def download_file(filename: str):
    return send_from_directory(
        app.config["RESULT_FOLDER"], filename, as_attachment=True, download_name=filename
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
