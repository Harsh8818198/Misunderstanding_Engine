from ai_integrations.LingoDev_client import LingoDevClient
from ai_integrations.language_detector import detect_language

lingo = LingoDevClient()


def auto_translate(text: str, target_lang: str):
    source_lang = detect_language(text)

    # LingoDev accepts "auto" as source
    if source_lang == "auto":
        source_lang = None

    translated = lingo.translate_text(
        text=text,
        source_lang=source_lang,
        target_lang=target_lang
    )

    return {
        "source_lang": source_lang or "auto",
        "target_lang": target_lang,
        "translated_text": translated
    }