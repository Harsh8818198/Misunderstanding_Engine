# ai_integrations/translator_client.py
"""
Translator client with configurable preference:
1) If LINGO_API_URL and LINGO_API_KEY are set in env, attempt Lingo.dev REST.
2) Otherwise use MyMemory free API.

Public API:
    translate_text(text, target_lang, source_lang=None) -> str
Raises TranslatorError on failure.
"""

import os
import requests
from typing import Optional

TIMEOUT = int(os.getenv("TRANSLATOR_TIMEOUT", "10"))

LINGO_API_URL = os.getenv("LINGO_API_URL")    # e.g. https://api.lingo.dev/v1/translate
LINGO_API_KEY = os.getenv("LINGO_API_KEY")

class TranslatorError(Exception):
    pass

def _call_lingo_rest(text: str, target_lang: str, source_lang: Optional[str] = None) -> str:
    """
    Conservative Lingo REST attempt. Only used if LINGO_API_URL+KEY are set.
    We do not assume any SDK. This tries to post JSON and extract typical fields.
    """
    if not LINGO_API_URL or not LINGO_API_KEY:
        raise TranslatorError("Lingo.dev credentials not configured")

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {LINGO_API_KEY}"}
    payload = {"text": text, "target_language": target_lang}
    if source_lang and source_lang != "auto":
        payload["source_language"] = source_lang

    resp = requests.post(LINGO_API_URL, json=payload, headers=headers, timeout=TIMEOUT)
    if resp.status_code >= 400:
        raise TranslatorError(f"Lingo REST error {resp.status_code}: {resp.text}")

    try:
        j = resp.json()
    except Exception:
        raise TranslatorError("Lingo returned non-JSON response")

    # Common response keys
    for key in ("translation", "translated_text", "result", "data"):
        if key in j:
            v = j[key]
            if isinstance(v, str):
                return v
            if isinstance(v, dict) and "translation" in v:
                return v["translation"]
    # fallback: first string value
    if isinstance(j, dict):
        for v in j.values():
            if isinstance(v, str):
                return v
    raise TranslatorError("Unexpected Lingo response structure")

def _call_mymemory(text: str, target_lang: str, source_lang: Optional[str] = None) -> str:
    """
    Call MyMemory free API.
    MyMemory requires a concrete source; it does not accept 'auto'.
    If source_lang is 'auto' or None, we will attempt to use 'en' as a pragmatic fallback.
    If source == target, skip call and return original text.
    """
    if not text:
        raise TranslatorError("No text to translate")

    src = source_lang if source_lang and source_lang != "auto" else "en"
    # avoid src == target
    if src.strip().lower() == target_lang.strip().lower():
        return text

    url = "https://api.mymemory.translated.net/get"
    params = {"q": text, "langpair": f"{src}|{target_lang}"}
    resp = requests.get(url, params=params, timeout=TIMEOUT)
    if resp.status_code >= 400:
        raise TranslatorError(f"MyMemory error {resp.status_code}: {resp.text}")

    try:
        j = resp.json()
    except Exception:
        raise TranslatorError("MyMemory returned non-JSON")

    if "responseData" in j and isinstance(j["responseData"], dict):
        tx = j["responseData"].get("translatedText")
        if tx:
            return tx

    raise TranslatorError(f"MyMemory response missing translated text: {j}")

def translate_text(text: str, target_lang: str, source_lang: Optional[str] = None) -> str:
    """
    Public function: tries Lingo REST if configured (and fails gracefully), then falls back to MyMemory.
    Raises TranslatorError on failure.
    """
    if not text:
        raise TranslatorError("Empty text")
    if not target_lang:
        raise TranslatorError("No target language provided")

    # Prefer Lingo if configured
    if LINGO_API_URL and LINGO_API_KEY:
        try:
            return _call_lingo_rest(text, target_lang, source_lang)
        except TranslatorError as e:
            # don't crash; fall back
            print(f"[translator_client] Lingo failed: {e}; falling back to MyMemory")

    # MyMemory fallback
    return _call_mymemory(text, target_lang, source_lang)
