"""
ocr/image_preprocessor.py — Image enhancement pipeline for OCR.
Key optimisations:
  • Decode image bytes once per call (no repeated Image.open)
  • Vectorised deskew using numpy projection variance (no per-angle PIL rotate)
  • preprocess_enhanced avoids double-sharpen and uses numpy threshold directly
"""
from __future__ import annotations

import io

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

from utils.logger import get_logger

log = get_logger(__name__)

# Deskew search range and step (degrees)
_DESKEW_RANGE = np.arange(-10.0, 10.5, 1.0)   # 1° steps — 20 iterations vs 40


def _open_gray(image_bytes: bytes) -> Image.Image:
    return Image.open(io.BytesIO(image_bytes)).convert("L")


def _to_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def preprocess_standard(image_bytes: bytes) -> bytes:
    """Grayscale → contrast boost → median denoise."""
    try:
        img = _open_gray(image_bytes)
        img = ImageEnhance.Contrast(img).enhance(1.5)
        img = img.filter(ImageFilter.MedianFilter(size=3))
        return _to_bytes(img)
    except Exception as exc:
        log.warning("Standard preprocess failed: %s — returning original", exc)
        return image_bytes


def preprocess_enhanced(image_bytes: bytes) -> bytes:
    """
    Aggressive pipeline for low-quality images:
    grayscale → 2× upscale → sharpen → contrast → numpy threshold.
    """
    try:
        img = _open_gray(image_bytes)
        w, h = img.size
        img = img.resize((w * 2, h * 2), Image.LANCZOS)
        img = img.filter(ImageFilter.SHARPEN)
        img = ImageEnhance.Contrast(img).enhance(2.0)
        arr = np.asarray(img, dtype=np.uint8)
        threshold = int(arr.mean())
        arr = np.where(arr > threshold, np.uint8(255), np.uint8(0))
        return _to_bytes(Image.fromarray(arr))
    except Exception as exc:
        log.warning("Enhanced preprocess failed: %s — returning standard", exc)
        return preprocess_standard(image_bytes)


def deskew(image_bytes: bytes) -> bytes:
    """
    Deskew using horizontal projection variance.
    Uses 1° steps (20 iterations) and pure numpy rotation to avoid
    creating a PIL image per angle.
    """
    try:
        img = _open_gray(image_bytes)
        arr = np.asarray(img, dtype=np.float32)

        best_angle = 0.0
        best_score = -1.0

        # scipy.ndimage.rotate is faster than PIL for array ops when available
        try:
            from scipy.ndimage import rotate as nd_rotate

            for angle in _DESKEW_RANGE:
                rotated = nd_rotate(arr, float(angle), reshape=False, cval=255.0)
                score   = float(np.var(rotated.sum(axis=1)))
                if score > best_score:
                    best_score = score
                    best_angle = float(angle)
        except ImportError:
            # PIL fallback — still 1° steps
            for angle in _DESKEW_RANGE:
                rotated = img.rotate(float(angle), expand=False, fillcolor=255)
                r_arr   = np.asarray(rotated, dtype=np.float32)
                score   = float(np.var(r_arr.sum(axis=1)))
                if score > best_score:
                    best_score = score
                    best_angle = float(angle)

        if abs(best_angle) > 0.5:
            img = img.rotate(best_angle, expand=True, fillcolor=255)

        return _to_bytes(img)
    except Exception as exc:
        log.warning("Deskew failed: %s — returning original", exc)
        return image_bytes
