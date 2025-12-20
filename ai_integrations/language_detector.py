# ai_integrations/language_detector.py
"""
Language detection wrapper.

Primary: langdetect (already in your requirements).
Optional: fasttext (if installed and model provided) for better accuracy on short/mixed text.
"""

from typing import Tuple
from langdetect import detect, DetectorFactory, LangDetectException
DetectorFactory.seed = 0

# Optional fasttext support (only if installed and model present)
try:
    import fasttext
    _HAS_FASTTEXT = True
except Exception:
    _HAS_FASTTEXT = False

_FASTTEXT_MODEL_PATH = "ai_integrations/lid.176.bin"  # optional; place model here if you use fasttext

def detect_language(text: str) -> Tuple[str, float]:
    """
    Detect language of `text`.
    Returns (lang_code, confidence).
    lang_code is ISO-639-1 when possible (e.g., 'en', 'hi').
    If detection fails returns ("auto", 0.0).
    """
    if not text or not text.strip():
        return "auto", 0.0

    text = text.strip()

    # Try fasttext if available and model exists
    if _HAS_FASTTEXT:
        try:
            model = fasttext.load_model(_FASTTEXT_MODEL_PATH)
            labels, probs = model.predict(text.replace("\n", " "), k=1)
            label = labels[0]  # e.g. '__label__en'
            lang = label.replace("__label__", "")
            confidence = float(probs[0])
            return lang, confidence
        except Exception:
            # fall back to langdetect
            pass

    # Fallback: langdetect
    try:
        code = detect(text)  # e.g., 'en', 'fr', 'hi'
        # Heuristic confidence: longer text -> higher confidence
        confidence = min(0.95, 0.3 + min(1.0, len(text) / 200.0))
        return code, confidence
    except LangDetectException:
        return "auto", 0.0
