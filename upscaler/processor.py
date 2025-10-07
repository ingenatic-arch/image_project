"""Image upscaling helpers."""
from __future__ import annotations

from pathlib import Path
from typing import BinaryIO

from PIL import Image

TARGET_WIDTH = 3840
TARGET_HEIGHT = 2160
TARGET_SIZE = (TARGET_WIDTH, TARGET_HEIGHT)


def _ensure_rgb(image: Image.Image) -> Image.Image:
    if image.mode in ("RGB", "RGBA"):
        return image.convert("RGB")
    return image.convert("RGB")


def upscale_to_4k(image: Image.Image) -> Image.Image:
    """Upscale the provided PIL image to a 4K (3840x2160) resolution.

    The implementation preserves aspect ratio while ensuring the final
    image is exactly 4K. Images that don't match the 16:9 ratio are
    center-cropped after resizing to fill the target size. Upscaling is
    performed using a high-quality Lanczos filter.
    """

    image = _ensure_rgb(image)

    width, height = image.size
    if width == TARGET_WIDTH and height == TARGET_HEIGHT:
        return image

    target_ratio = TARGET_WIDTH / TARGET_HEIGHT
    source_ratio = width / height if height else target_ratio

    if source_ratio > target_ratio:
        scale = TARGET_HEIGHT / height
    else:
        scale = TARGET_WIDTH / width

    resized_width = max(int(round(width * scale)), TARGET_WIDTH)
    resized_height = max(int(round(height * scale)), TARGET_HEIGHT)

    resized = image.resize((resized_width, resized_height), Image.LANCZOS)

    if resized_width == TARGET_WIDTH and resized_height == TARGET_HEIGHT:
        return resized

    if resized_width < TARGET_WIDTH or resized_height < TARGET_HEIGHT:
        canvas = Image.new("RGB", TARGET_SIZE)
        offset = (
            max((TARGET_WIDTH - resized_width) // 2, 0),
            max((TARGET_HEIGHT - resized_height) // 2, 0),
        )
        canvas.paste(resized, offset)
        return canvas

    left = max((resized_width - TARGET_WIDTH) // 2, 0)
    upper = max((resized_height - TARGET_HEIGHT) // 2, 0)
    right = left + TARGET_WIDTH
    lower = upper + TARGET_HEIGHT

    return resized.crop((left, upper, right, lower))


def upscale_image_file(source: BinaryIO | Path, destination: BinaryIO | Path) -> None:
    """Upscale an image from ``source`` and write it to ``destination``.

    ``source`` and ``destination`` can be either file-like objects or
    paths on disk.
    """

    if isinstance(source, (str, Path)):
        with Image.open(source) as img:
            upscaled = upscale_to_4k(img)
            _save_image(upscaled, destination)
            return

    with Image.open(source) as img:
        upscaled = upscale_to_4k(img)
        _save_image(upscaled, destination)


def _save_image(image: Image.Image, destination: BinaryIO | Path) -> None:
    if isinstance(destination, (str, Path)):
        dest_path = Path(destination)
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        image.save(dest_path, format="PNG")
    else:
        image.save(destination, format="PNG")
        destination.seek(0)
