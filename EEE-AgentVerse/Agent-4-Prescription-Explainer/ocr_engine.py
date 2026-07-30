# ocr_engine.py - Prescription OCR using Gemini Vision (primary) + regex fallback
# Gemini Vision reads ANY image — handwritten, printed, blurry, rotated.
# No EasyOCR or Tesseract required.

import re
import os
import base64
import logging
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
logger = logging.getLogger(__name__)

_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# ---------------------------------------------------------------------------
# Gemini Vision — reads prescription image directly
# ---------------------------------------------------------------------------

_VISION_PROMPT = """You are a medical OCR assistant. Read this prescription image carefully.
Extract ALL text you can see, including handwritten text.

Then return a JSON object with these exact fields:
{
  "doctor": "doctor name if visible",
  "hospital": "hospital or clinic name if visible",
  "date": "date if visible",
  "patient": "patient name if visible",
  "medicines": ["list of medicine names"],
  "dosage": ["list of dosages matching medicines"],
  "frequency": ["list of frequencies like once daily, twice daily"],
  "duration": ["list of durations like 5 days, 1 week"],
  "instructions": ["list of instructions like after food, before food"],
  "raw_text": "all text you could read from the image"
}

Rules:
- For handwritten prescriptions, do your best to read the text
- If a field is not visible, use empty string "" or empty list []
- Return ONLY the JSON, no other text
- medicines list should have actual drug names, not abbreviations like Tab or Cap
"""


def _gemini_vision_ocr(image_bytes: bytes) -> dict:
    """Use Gemini Vision to read prescription image. Returns structured dict."""
    if not _API_KEY or _API_KEY == "your_gemini_api_key_here":
        raise ValueError("No Gemini API key configured")

    # Try new SDK first
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=_API_KEY)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                _VISION_PROMPT,
            ],
        )
        return _parse_gemini_response(response.text)
    except Exception as e1:
        logger.warning("Gemini new SDK vision failed: %s", e1)

    # Try old SDK with PIL
    try:
        import google.generativeai as genai_old
        import PIL.Image, io
        genai_old.configure(api_key=_API_KEY)
        model = genai_old.GenerativeModel("gemini-1.5-flash")
        img = PIL.Image.open(io.BytesIO(image_bytes))
        response = model.generate_content([_VISION_PROMPT, img])
        return _parse_gemini_response(response.text)
    except Exception as e2:
        logger.warning("Gemini old SDK vision failed: %s", e2)
        raise RuntimeError(f"Gemini Vision failed: {e2}")


def _parse_gemini_response(text: str) -> dict:
    """Parse JSON from Gemini response."""
    import json
    # Strip markdown fences
    cleaned = re.sub(r"```(?:json)?|```", "", text).strip()
    # Find first {...}
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        raise ValueError("No JSON in Gemini response")
    data = json.loads(match.group())
    # Ensure all expected keys exist
    for key in ["doctor", "hospital", "date", "patient", "raw_text"]:
        data.setdefault(key, "")
    for key in ["medicines", "dosage", "frequency", "duration", "instructions"]:
        data.setdefault(key, [])
    return data


# ---------------------------------------------------------------------------
# Regex fallback (no external OCR library needed)
# ---------------------------------------------------------------------------

_DATE_RE = re.compile(
    r"\b(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}|\d{4}[\/\-\.]\d{1,2}[\/\-\.]\d{1,2})\b"
)
_DOSAGE_RE = re.compile(
    r"\b(\d+(?:\.\d+)?\s*(?:mg|mcg|ml|g|iu|units?|tab(?:let)?s?|cap(?:sule)?s?))\b",
    re.IGNORECASE,
)
_FREQ_RE = re.compile(
    r"\b(once\s+daily|twice\s+daily|three\s+times\s+daily|od|bd|tds|qid|sos|prn|"
    r"every\s+\d+\s+hours?|at\s+(?:night|bedtime|morning))\b",
    re.IGNORECASE,
)
_DURATION_RE = re.compile(
    r"\b(\d+\s*(?:days?|weeks?|months?|wks?|mths?))\b", re.IGNORECASE
)
_DR_RE = re.compile(
    r"(?:dr\.?|doctor)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", re.IGNORECASE
)
_PATIENT_RE = re.compile(
    r"(?:patient|name|pt\.?)\s*[:\-]?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
    re.IGNORECASE,
)
_MED_PREFIXES = ["tab", "cap", "syp", "inj", "oint", "drop", "susp"]


def _regex_extract(raw_text: str) -> dict:
    lines = [l.strip() for l in raw_text.splitlines() if l.strip()]
    doctor = hospital = date = patient = ""
    medicines, dosages, frequencies, durations, instructions = [], [], [], [], []

    for line in lines:
        if not doctor:
            m = _DR_RE.search(line)
            if m:
                doctor = m.group(1).strip()
        if not date:
            m = _DATE_RE.search(line)
            if m:
                date = m.group(0)
        if not patient:
            m = _PATIENT_RE.search(line)
            if m:
                patient = m.group(1).strip()
        ll = line.lower()
        if any(ll.startswith(p) for p in _MED_PREFIXES) or (
            _DOSAGE_RE.search(line) and len(line) < 80
        ):
            medicines.append(line)
        dosages.extend(_DOSAGE_RE.findall(line))
        frequencies.extend(_FREQ_RE.findall(line))
        durations.extend(_DURATION_RE.findall(line))

    return {
        "doctor": doctor, "hospital": hospital, "date": date, "patient": patient,
        "medicines": medicines,
        "dosage": list(dict.fromkeys(dosages)),
        "frequency": list(dict.fromkeys(frequencies)),
        "duration": list(dict.fromkeys(durations)),
        "instructions": list(dict.fromkeys(instructions)),
        "raw_text": raw_text,
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_prescription(image_bytes: bytes, max_retries: int = 3) -> dict:
    """
    Main entry point.
    1. Try Gemini Vision (reads ANY image — handwritten, printed, blurry)
    2. Fallback: EasyOCR → Tesseract → regex
    Returns structured dict, never raises.
    """

    # ── Primary: Gemini Vision ──────────────────────────────────────────────
    try:
        fields = _gemini_vision_ocr(image_bytes)
        raw    = fields.pop("raw_text", "")
        score  = _score(fields)
        logger.info("Gemini Vision OCR score=%.2f", score)
        return {
            "raw_text":   raw,
            "fields":     fields,
            "confidence": max(score, 0.75),   # Gemini is reliable
            "ocr_engine": "Gemini Vision",
            "strategy":   0,
        }
    except Exception as e:
        logger.warning("Gemini Vision OCR failed: %s", e)

    # ── Fallback 1: EasyOCR ─────────────────────────────────────────────────
    try:
        import numpy as np
        import cv2
        arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        denoised = cv2.fastNlMeansDenoising(gray, h=15)
        processed = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 10
        )
        import easyocr
        reader = easyocr.Reader(["en"], gpu=False, verbose=False)
        results = reader.readtext(processed, detail=1, paragraph=False)
        raw = "\n".join(r[1] for r in results)
        conf = float(np.mean([r[2] for r in results])) if results else 0.0
        fields = _regex_extract(raw)
        score = _score(fields, conf)
        return {"raw_text": raw, "fields": fields, "confidence": score,
                "ocr_engine": "EasyOCR", "strategy": 1}
    except Exception as e:
        logger.warning("EasyOCR failed: %s", e)

    # ── Fallback 2: Tesseract ───────────────────────────────────────────────
    try:
        import numpy as np
        import cv2
        import pytesseract
        arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, processed = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        data = pytesseract.image_to_data(
            processed, config="--oem 3 --psm 6",
            output_type=pytesseract.Output.DICT
        )
        words = [w for w in data["text"] if w.strip()]
        confs = [c for c, w in zip(data["conf"], data["text"])
                 if w.strip() and int(c) >= 0]
        raw = " ".join(words)
        conf = float(np.mean(confs)) / 100.0 if confs else 0.0
        fields = _regex_extract(raw)
        score = _score(fields, conf)
        return {"raw_text": raw, "fields": fields, "confidence": score,
                "ocr_engine": "Tesseract", "strategy": 2}
    except Exception as e:
        logger.warning("Tesseract failed: %s", e)

    # ── Total failure ───────────────────────────────────────────────────────
    return {
        "raw_text": "", "fields": {
            "doctor": "", "hospital": "", "date": "", "patient": "",
            "medicines": [], "dosage": [], "frequency": [],
            "duration": [], "instructions": [],
        },
        "confidence": 0.0, "ocr_engine": "none", "strategy": -1,
        "error": (
            "Could not read the prescription. "
            "Please add your GEMINI_API_KEY to the .env file for best results, "
            "or upload a clearer image."
        ),
    }


def _score(fields: dict, ocr_conf: float = 0.8) -> float:
    filled = sum(1 for v in fields.values() if v)
    return round(0.6 * ocr_conf + 0.4 * (filled / max(len(fields), 1)), 3)
