# src/translation_pipeline.py
from typing import Dict, Any, Optional
from ai_integrations.language_detector import detect_language
from ai_integrations.translator_client import translate_text, TranslatorError

def translate_and_package(text: str, target_lang: str, force_source: Optional[str] = None) -> Dict[str, Any]:
    """
    Detects source (unless force_source given), translates, and returns structured result.
    Result shape:
      {
        "detected_lang": "hi",
        "detection_confidence": 0.8,
        "target_lang": "en",
        "translated_text": "...",
        "error": None
      }
    """
    if force_source:
        source_lang = force_source
        confidence = 1.0
    else:
        source_lang, confidence = detect_language(text)

    out = {
        "detected_lang": source_lang or "auto",
        "detection_confidence": confidence,
        "target_lang": target_lang,
        "translated_text": None,
        "error": None
    }

    try:
        translated = translate_text(text, target_lang, source_lang)
        out["translated_text"] = translated
    except TranslatorError as te:
        out["error"] = str(te)
    except Exception as e:
        out["error"] = f"Unexpected translation error: {e}"

    return out
