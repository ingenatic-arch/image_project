# 4K Image Upscaler Web App

This project provides a simple Flask web application that lets you upload an
image, upscale it to a 4K resolution (3840×2160), and download the processed
file. Upscaling is handled by the utilities in the `upscaler/` package using
Pillow's high-quality resizing filters.

## Requirements

- Python 3.11+
- [Pipenv](https://pipenv.pypa.io/) or `pip`

Install the Python dependencies:

```bash
pip install -r requirements.txt
```

## Running the app

```bash
export FLASK_APP=app.py
flask run --host=0.0.0.0 --port=5000
```

Then open <http://localhost:5000> in your browser.

## Project structure

```
app.py              # Flask entry point
upscaler/           # Image upscaling helpers
templates/          # HTML templates
static/             # CSS and other static assets
uploads/            # Temporary uploads (ignored by git)
generated/          # Upscaled output images (ignored by git)
```
