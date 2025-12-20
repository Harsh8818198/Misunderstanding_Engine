# Add this import at the top with your other imports
from routes.translator_routes import bp as translator_bp

# Register the blueprint (add this after your other blueprint registrations)

from langdetect import detect, DetectorFactory
from deep_translator import GoogleTranslator
from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
from ai_integrations.gemini_client import OpenRouterAnalyzer
from ai_integrations.lingodev_client import LingoDevClient
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.register_blueprint(translator_bp)
import requests


load_dotenv()
# Add after load_dotenv()
print(f"🔑 API Key loaded: {os.getenv('OPENROUTER_API_KEY')[:20]}..." if os.getenv('OPENROUTER_API_KEY') else "❌ No API key found!")


def analyze_text_internal(text: str) -> dict:
    """
    Internal function to analyze text
    This wraps your existing /analyze endpoint logic
    so translate-and-analyze can call it programmatically

    Returns the same JSON structure as your /analyze endpoint
    """
    # Import your existing analysis modules here
    # Example:
    # from ai_integrations.OpenRouter_client import openrouter
    # from ai_integrations.LingoDev_client import lingodev

    # Call your existing analysis logic
    # This should match what your /analyze endpoint does

    # Example structure (adjust to match your actual code):
    try:
        # Your existing analysis logic here
        emotion_analysis = openrouter.analyze_emotion(text)
        ambiguity_score = openrouter.calculate_ambiguity_score(text)
        misunderstandings = openrouter.generate_misunderstandings(text, emotion_analysis)
        improved_version = openrouter.suggest_improvement(text, emotion_analysis)

        return {
            'status': 'success',
            'original_text': text,
            'emotion_analysis': emotion_analysis,
            'ambiguity_score': ambiguity_score,
            'misunderstandings': misunderstandings,
            'improved_version': improved_version
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }
def analyze_emotions(original_text, translated_text, source_lang, target_lang):
    """Analyze emotions in both original and translated text"""
    try:
        api_key = os.getenv('OPENROUTER_API_KEY')

        prompt = f"""Analyze the emotional tone of these texts:

Original ({source_lang}): {original_text}
Translated ({target_lang}): {translated_text}

Provide:
1. Original emotion: (joy/sadness/anger/neutral/optimism)
2. Translated emotion: (joy/sadness/anger/neutral/optimism)
3. Misunderstanding risk: (Low/Medium/High)
4. Explanation: Brief reason for any mismatch

Format: JSON only"""

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "meta-llama/llama-3.1-8b-instruct:free",
                "messages": [{"role": "user", "content": prompt}]
            }
        )

        result = response.json()
        analysis = result['choices'][0]['message']['content']

        return analysis

    except Exception as e:
        return {
            'original_emotion': 'neutral',
            'translated_emotion': 'neutral',
            'risk': 'Low',
            'explanation': 'Analysis unavailable'
        }
# Initialize AI clients
try:
    openrouter = OpenRouterAnalyzer()
    lingodev = LingoDevClient()
    print("✅ AI services initialized successfully!")
except Exception as e:
    print(f"⚠️ AI initialization error: {e}")
    openrouter = None
    lingodev = None


@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')


@app.route('/analysis')
def analysis():
    """Results page"""
    return render_template('analysis.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    """API endpoint for text analysis"""
    data = request.json
    text = data.get('text', '')

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    # If OpenRouter not available, return mock data
    if not openrouter:
        return jsonify({
            'status': 'error',
            'message': 'AI service not configured',
            'original_text': text,
            'using_mock': True
        })

    try:
        print(f"\n{'=' * 50}")
        print(f"🔍 Analyzing: {text[:100]}...")
        print(f"{'=' * 50}")

        # Step 1: Language detection (LingoDev)
        print("1️⃣ Detecting language...")
        language_info = lingodev.detect_language(text) if lingodev else {"language": "en"}
        print(f"   └─ Language: {language_info.get('language', 'en')}")

        # Step 1.5: Translation to English (LingoDev)
        print("🌍 Translating text to English for standardized analysis...")
        source_lang = language_info.get("language", "en")
        # Step 1.5: Translation to English (LingoDev)
        print("🌍 Translating text to English for standardized analysis...")
        source_lang = language_info.get("language", "en")

        try:
            translated_text = lingodev.translate_with_context(text, target_lang="en") if lingodev else text
        except Exception as e:
            print(f"Translation failed: {e}. Using original text.")
            translated_text = text

        print(f"   └─ Translated text: {translated_text[:100]}...")

        # Step 2: Emotion analysis (OpenRouter)
        print("2️⃣ Analyzing emotions...")
        emotion_analysis = openrouter.analyze_emotion(text)
        print(f"   └─ Primary emotion: {emotion_analysis.get('primary_emotion')}")

        # Step 3: Ambiguity score (OpenRouter)
        print("3️⃣ Calculating ambiguity...")
        ambiguity_score = openrouter.calculate_ambiguity_score(text)
        print(f"   └─ Ambiguity score: {ambiguity_score}/10")

        # Step 4: Generate misunderstandings (OpenRouter)
        print("4️⃣ Generating misunderstandings...")
        misunderstandings = openrouter.generate_misunderstandings(
            text,
            emotion_analysis,
            count=5
        )
        print(f"   └─ Generated {len(misunderstandings)} scenarios")

        # Step 5: Suggest improvement (OpenRouter)
        print("5️⃣ Creating improved version...")
        improved_version = openrouter.suggest_improvement(text, emotion_analysis)
        print(f"   └─ Improvement ready")

        # Step 6: Cultural context (LingoDev)
        cultural_context = lingodev.get_cultural_context(
            text=translated_text,
        )

        # Calculate risk level
        risk_level = "HIGH" if ambiguity_score >= 7 else "MEDIUM" if ambiguity_score >= 4 else "LOW"

        # Calculate clarity improvement
        clarity_improvement = min(int((10 - ambiguity_score) * 10), 95)

        # Prepare final response
        response = {
            'status': 'success',
            'original_text': text,
            'translated_text': translated_text,
            'language_info': language_info,
            'emotion_analysis': {
                'primary_emotion': emotion_analysis.get('primary_emotion', 'neutral'),
                'intensity': emotion_analysis.get('intensity', 5.0),
                'emotions': emotion_analysis.get('emotions_detected', ['neutral']),
                'hidden_feelings': emotion_analysis.get('hidden_feelings', ''),
                'tone_markers': emotion_analysis.get('tone_markers', [])
            },
            'ambiguity_score': round(ambiguity_score, 1),
            'misunderstanding_risk': risk_level,
            'misunderstandings': misunderstandings,
            'improved_version': improved_version,
            'clarity_improvement': clarity_improvement,
            'cultural_context': cultural_context,
            'using_mock': False
        }

        print(f"\n✅ Analysis complete!")
        print(f"{'=' * 50}\n")

        return jsonify(response)

    except Exception as e:
        print(f"\n❌ Error during analysis: {e}\n")
        import traceback
        traceback.print_exc()

        return jsonify({
            'error': str(e),
            'message': 'Analysis failed. Please try again.',
            'original_text': text,
            'using_mock': True
        }), 500


@app.route('/test-api', methods=['GET'])
def test_api():
    """Test endpoint to verify all APIs"""
    results = {
        'openrouter': False,
        'lingodev': False
    }

    # Test OpenRouter
    if openrouter:
        results['openrouter'] = openrouter.test_connection()

    # Test LingoDev
    if lingodev:
        try:
            test = lingodev.detect_language("Hello")
            results['lingodev'] = test.get('language') is not None
        except:
            results['lingodev'] = False

    status = 'success' if all(results.values()) else 'partial'

    return jsonify({
        'status': status,
        'services': results,
        'message': f"OpenRouter: {'✅' if results['openrouter'] else '❌'}, LingoDev: {'✅' if results['lingodev'] else '❌'}"
    })


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🚀 The Misunderstanding Engine - Starting Server")
    print("=" * 60)
    print(f"🌐 URL: http://127.0.0.1:5000")
    print(f"🧪 Test API: http://127.0.0.1:5000/test-api")
    print("=" * 60 + "\n")

    app.run(debug=True, port=5000)
