import math
from scipy.spatial.distance import cosine

# Language to culture mapping
LANG_TO_CULTURE = {
    "ja": "JP",  # Japanese
    "en": "US",  # English (US)
    "hi": "IN",  # Hindi (India)
    "pt": "BR",  # Portuguese (Brazil)
    "fr": "FR",  # French
    "ar": "AR",  # Arabic
    "es": "ES",  # Spanish
    "de": "DE",  # German
    "zh": "CN",  # Chinese
}


def lang_to_culture_map(lang):
    """Map language code to culture code."""
    return LANG_TO_CULTURE.get(lang, "US")


def apply_multipliers(emotion_vec, multipliers):
    """
    Apply cultural multipliers to emotion vector.

    emotion_vec: dict {emotion: probability}
    multipliers: dict {emotion: multiplier}

    Returns: adjusted emotion dict (normalized to sum=1)
    """
    adjusted = {}
    for emotion, prob in emotion_vec.items():
        multiplier = multipliers.get(emotion, 1.0)
        adjusted[emotion] = float(prob) * float(multiplier)

    # Normalize to sum to 1.0
    total = sum(adjusted.values())
    if total <= 0:
        return {k: 0.0 for k in adjusted}

    return {k: adjusted[k] / total for k in adjusted}


def compute_misunderstanding_risk(src_vec, tgt_vec):
    """
    Calculate misunderstanding risk (0-100) between source and target emotions.
    Uses cosine distance and max difference.
    """
    # Get all emotion keys
    keys = sorted(list(set(list(src_vec.keys()) + list(tgt_vec.keys()))))

    # Convert to vectors
    v1 = [src_vec.get(k, 0.0) for k in keys]
    v2 = [tgt_vec.get(k, 0.0) for k in keys]

    try:
        # Cosine distance (0=same, 1=orthogonal)
        cos_dist = cosine(v1, v2)
    except Exception:
        # Fallback to normalized Euclidean
        cos_dist = math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2))) / math.sqrt(len(v1))

    # Maximum single-emotion difference
    max_diff = max(abs(a - b) for a, b in zip(v1, v2))

    # Combined risk score
    risk = cos_dist * 100 + max_diff * 50
    risk = max(0.0, min(100.0, risk))

    return round(risk, 1)


def generate_explanation(src_vec, tgt_vec, risk):
    """Generate human-readable explanation of the analysis."""
    # Find dominant emotions
    src_top = max(src_vec.items(), key=lambda x: x[1])[0]
    tgt_top = max(tgt_vec.items(), key=lambda x: x[1])[0]

    # Risk level categorization
    if risk > 60:
        level = "High"
        advice = "Consider rephrasing or follow-up to avoid misinterpretation."
    elif risk > 30:
        level = "Medium"
        advice = "Possible mismatch; double-check tone."
    else:
        level = "Low"
        advice = "Message likely to be interpreted as intended."

    return (f"Risk: {risk}% ({level}). "
            f"Source dominant emotion: {src_top}. "
            f"Perceived dominant: {tgt_top}. {advice}")