# routes/translator_routes.py
from flask import Blueprint, request, jsonify
from src.translation_pipeline import translate_and_package

# Import analyze_text explicitly. Ensure this file exists.
from src.model_inference import analyze_text

bp = Blueprint("translator", __name__)

@bp.route("/api/translate", methods=["POST"])
def api_translate():
    data = request.get_json(force=True)
    text = data.get("text")
    target = data.get("target")
    force_source = data.get("source")  # optional

    if not text or not target:
        return jsonify({"error": "text and target are required"}), 400

    result = translate_and_package(text, target, force_source)
    status = 200 if result.get("error") is None else 500
    return jsonify(result), status

@bp.route("/api/translate-and-analyze", methods=["POST"])
def api_translate_and_analyze():
    data = request.get_json(force=True)
    text = data.get("text")
    target = data.get("target")
    force_source = data.get("source")  # optional
    run_analysis = bool(data.get("run_analysis", True))

    if not text or not target:
        return jsonify({"error": "text and target are required"}), 400

    translation = translate_and_package(text, target, force_source)
    response_payload = {"translation": translation}

    # If translation failed, return it and error
    if translation.get("error"):
        return jsonify(response_payload), 500

    if run_analysis:
        try:
            analysis_result = analyze_text(translation["translated_text"])
            response_payload["analysis"] = analysis_result
        except Exception as e:
            response_payload["analysis_error"] = f"Analysis failed: {e}"
            return jsonify(response_payload), 500

    return jsonify(response_payload), 200
