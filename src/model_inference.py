# src/model_inference.py
"""
Model inference adapter for Misunderstanding Engine.
Updated to use Gemini API as the primary analyzer.

Exports analyze_text(text) which returns a JSON-serializable dict.
"""

import os
from typing import Dict, Any

# Import Gemini client
try:
    from ai_integrations.gemini_client import GeminiClient

    _GEMINI_AVAILABLE = True
except ImportError:
    _GEMINI_AVAILABLE = False
    print("[model_inference] Warning: Gemini client not available")

# Lazy-load Gemini client
_GEMINI_CLIENT = None


def _get_gemini_client() -> 'GeminiClient':
    """Get or create Gemini client singleton"""
    global _GEMINI_CLIENT
    if _GEMINI_CLIENT is None:
        if not _GEMINI_AVAILABLE:
            raise RuntimeError("Gemini client not available")
        _GEMINI_CLIENT = GeminiClient()
    return _GEMINI_CLIENT


def analyze_text(text: str) -> Dict[str, Any]:
    """
    Primary entrypoint used by routes/translator_routes.py.

    Returns:
      {
         "emotion_probs": {...},
         "primary_emotion": "...",
         "misunderstanding_risk": 0.32,
         "notes": [...],
         "raw_text": text
      }

    Uses Gemini API for analysis, with fallback to heuristics if unavailable.
    """
    text = (text or "").strip()
    if not text:
        return {
            "emotion_probs": {},
            "primary_emotion": "neutral",
            "misunderstanding_risk": 0.0,
            "notes": ["empty input"],
            "raw_text": text
        }

    # Try Gemini analysis
    try:
        if _GEMINI_AVAILABLE:
            client = _get_gemini_client()
            gemini_result = client.analyze_communication(text)

            # Convert Gemini response to expected format
            emotion = gemini_result.get('emotion', 'neutral')
            ambiguity_score = gemini_result.get('ambiguity_score', 5.0)

            # Map emotion to probability format (for backward compatibility)
            emotion_probs = {
                emotion: 0.8,  # Primary emotion gets high probability
                'neutral': 0.2 if emotion != 'neutral' else 0.8
            }

            # Calculate misunderstanding risk from ambiguity score
            # Scale: 0-10 -> 0.0-1.0
            risk = min(1.0, ambiguity_score / 10.0)

            # Extract notes from clarity issues
            notes = gemini_result.get('clarity_issues', [])
            if not notes:
                if ambiguity_score > 7:
                    notes.append("High ambiguity detected in message")
                elif ambiguity_score > 4:
                    notes.append("Some ambiguity present in message")
                else:
                    notes.append("Message is relatively clear")

            return {
                "emotion_probs": emotion_probs,
                "primary_emotion": emotion,
                "misunderstanding_risk": round(risk, 3),
                "notes": notes,
                "raw_text": text,
                "gemini_analysis": gemini_result  # Include full Gemini response
            }

    except Exception as e:
        print(f"[model_inference] Gemini analysis error: {e}")
        # Fall through to heuristic fallback

    # Fallback heuristic analysis
    return _heuristic_analysis(text)


def _heuristic_analysis(text: str) -> Dict[str, Any]:
    """
    Fallback heuristic analysis when Gemini is unavailable.
    Uses simple rules to estimate emotion and risk.
    """
    lowered = text.lower()
    is_question = text.endswith('?')
    words = text.split()
    word_count = len(words)
    uppercase_ratio = sum(1 for ch in text if ch.isupper()) / max(1, len(text))

    # Determine sentiment
    if any(w in lowered for w in ("sorry", "apolog", "regret", "sad", "unhappy")):
        sentiment = "sadness"
    elif any(w in lowered for w in ("angry", "mad", "furious", "hate")):
        sentiment = "anger"
    elif any(w in lowered for w in ("great", "happy", "good", "thanks", "excellent", "wonderful")):
        sentiment = "joy"
    elif any(w in lowered for w in ("hope", "optimistic", "positive", "confident")):
        sentiment = "optimism"
    else:
        sentiment = "neutral"

    # Calculate risk score
    risk_score = 0.1
    if is_question:
        risk_score += 0.15
    if word_count < 5:
        risk_score += 0.2
    if uppercase_ratio > 0.3:
        risk_score += 0.1
    if any(w in lowered for w in ("idiom", "sarcasm", "lol", "jk", "maybe", "kinda")):
        risk_score += 0.25
    risk_score = min(1.0, round(risk_score, 3))

    # Generate notes
    notes = []
    if is_question:
        notes.append("Text is a question – may be ambiguous")
    if word_count < 5:
        notes.append("Very short text – detection/translation may be unreliable")
    if uppercase_ratio > 0.3:
        notes.append("High uppercase ratio – tone may be perceived as shouting")
    if not notes:
        notes.append("Using heuristic analysis (Gemini unavailable)")

    # Create emotion probabilities
    emotion_probs = {sentiment: 0.7}
    for emo in ["joy", "sadness", "anger", "neutral", "optimism"]:
        if emo not in emotion_probs:
            emotion_probs[emo] = 0.1

    return {
        "emotion_probs": emotion_probs,
        "primary_emotion": sentiment,
        "misunderstanding_risk": risk_score,
        "notes": notes,
        "raw_text": text,
        "using_fallback": True
    }


# Test function
if __name__ == "__main__":
    print("Testing model_inference with Gemini...")

    test_texts = [
        "I'm fine....",
        "This is great!",
        "I'm so angry right now",
        "Maybe we could try?",
        "k"
    ]

    for text in test_texts:
        print(f"\n{'=' * 50}")
        print(f"Text: {text}")
        result = analyze_text(text)
        print(f"Emotion: {result['primary_emotion']}")
        print(f"Risk: {result['misunderstanding_risk']}")
        print(f"Notes: {result['notes']}")