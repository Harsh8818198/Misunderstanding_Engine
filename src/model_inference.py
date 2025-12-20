# src/model_inference.py
"""
Model inference adapter for Misunderstanding Engine.

Exports analyze_text(text) which returns a JSON-serializable dict.
It uses a lazy-loaded TensorFlow transformer classifier (ModelInference)
and falls back to a lightweight heuristic analysis if model loading fails.
"""

import os
from typing import Dict, Any

# Keep the model classname logic you had, but adapt to module-level usage.
# Note: this lazy-loads the TF model only when analyze_text is called.
try:
    import tensorflow as tf
    from transformers import AutoTokenizer, TFAutoModelForSequenceClassification
    import numpy as np
    _TF_AVAILABLE = True
except Exception:
    _TF_AVAILABLE = False

# -- Model wrapper (lazy)
class ModelInference:
    def __init__(self, model_name: str):
        # Minimal init logs
        print(f"[ModelInference] Loading model: {model_name} ...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = TFAutoModelForSequenceClassification.from_pretrained(model_name, from_pt=True)
        # keep consistent label set (your model)
        self.labels = ["anger", "joy", "optimism", "sadness"]
        print("[ModelInference] Model loaded.")

    def predict_emotion(self, text: str) -> Dict[str, float]:
        if not text or not text.strip():
            return {lbl: 0.0 for lbl in self.labels}
        try:
            inputs = self.tokenizer(
                text,
                return_tensors="tf",
                truncation=True,
                padding=True,
                max_length=512,
            )
            outputs = self.model(inputs)
            # outputs.logits may be a Tensor
            logits = outputs.logits.numpy()[0]
            probs = tf.nn.softmax(logits).numpy()
            # normalize to expected label length
            if len(probs) >= len(self.labels):
                probs = probs[:len(self.labels)]
            else:
                probs = np.pad(probs, (0, len(self.labels) - len(probs)))
            return {lbl: float(p) for lbl, p in zip(self.labels, probs)}
        except Exception as e:
            print(f"[ModelInference] prediction error: {e}")
            return {lbl: 0.0 for lbl in self.labels}


# module-level lazy singleton
_MODEL_INSTANCE = None

def _get_model_instance() -> ModelInference:
    global _MODEL_INSTANCE
    if _MODEL_INSTANCE is None:
        # model name from env or fallback to a small local/test model
        model_name = os.getenv("EMOTION_MODEL_NAME", "distilbert-base-uncased")  # replace with your model if needed
        if not _TF_AVAILABLE:
            raise RuntimeError("TensorFlow/transformers not available in this environment.")
        _MODEL_INSTANCE = ModelInference(model_name)
    return _MODEL_INSTANCE


# Public function expected by routes
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
    This will call your real analyzer (TF model) if available; otherwise returns a heuristic fallback.
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

    # Try real model (if available)
    try:
        if _TF_AVAILABLE:
            model = _get_model_instance()
            probs = model.predict_emotion(text)  # dict of {label:prob}
            # Primary emotion = label with highest prob
            primary = max(probs.items(), key=lambda kv: kv[1])[0] if probs else "neutral"
            # crude risk heuristics using emotion + length
            word_count = len(text.split())
            risk = 0.1
            if primary in ("anger", "sadness"):
                risk += 0.3
            if word_count < 5:
                risk += 0.2
            risk = min(1.0, round(risk, 3))

            notes = []
            if word_count < 5:
                notes.append("Very short message: may be ambiguous.")
            if primary == "anger":
                notes.append("Detected anger: risk of confrontation.")
            if primary == "sadness":
                notes.append("Detected sadness: may be misinterpreted as withdrawn.")

            return {
                "emotion_probs": probs,
                "primary_emotion": primary,
                "misunderstanding_risk": risk,
                "notes": notes,
                "raw_text": text
            }

    except Exception as e:
        # if the model failed to load/predict, log and fall through to heuristic fallback
        print(f"[model_inference] model error: {e}")

    # Fallback heuristic analysis (safe)
    lowered = text.lower()
    is_question = text.endswith('?')
    words = text.split()
    word_count = len(words)
    uppercase_ratio = sum(1 for ch in text if ch.isupper()) / max(1, len(text))

    if any(w in lowered for w in ("sorry", "apolog", "regret", "sad")):
        sentiment = "negative"
    elif any(w in lowered for w in ("great", "happy", "good", "thanks")):
        sentiment = "positive"
    else:
        sentiment = "neutral"

    risk_score = 0.1
    if is_question:
        risk_score += 0.15
    if word_count < 5:
        risk_score += 0.2
    if uppercase_ratio > 0.3:
        risk_score += 0.1
    if any(w in lowered for w in ("idiom", "sarcasm", "lol", "jk")):
        risk_score += 0.25
    risk_score = min(1.0, round(risk_score, 3))

    notes = []
    if is_question:
        notes.append("text is a question — may be ambiguous")
    if word_count < 5:
        notes.append("very short text — detection/translation may be unreliable")
    if uppercase_ratio > 0.3:
        notes.append("high uppercase ratio — tone may be perceived as shouting")

    return {
        "emotion_probs": {},
        "primary_emotion": sentiment,
        "misunderstanding_risk": risk_score,
        "notes": notes,
        "raw_text": text
    }
