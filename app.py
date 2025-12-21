# app.py - Updated for Gemini API

from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
from langdetect import detect, DetectorFactory
from deep_translator import GoogleTranslator

# Import Gemini client instead of OpenRouter
from ai_integrations.gemini_client import GeminiClient
from ai_integrations.lingodev_client import LingoDevClient
from routes.translator_routes import bp as translator_bp

load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.register_blueprint(translator_bp)

# Check API key
gemini_key = os.getenv('GEMINI_API_KEY')
print(f"🔑 API Key loaded: {gemini_key[:20]}..." if gemini_key else "❌ No Gemini API key found!")

# Initialize AI clients
try:
    gemini_client = GeminiClient()
    lingodev = LingoDevClient()
    print("✅ AI services initialized successfully!")
except Exception as e:
    print(f"⚠️ AI initialization error: {e}")
    gemini_client = None
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

    # If Gemini not available, return error
    if not gemini_client:
        return jsonify({
            'status': 'error',
            'message': 'Gemini API service not configured',
            'original_text': text,
            'using_mock': True
        }), 500

    try:
        print(f"\n{'=' * 50}")
        print(f"🔍 Analyzing: {text[:100]}...")
        print(f"{'=' * 50}")

        # Step 1: Language detection (LingoDev)
        print("1️⃣ Detecting language...")
        language_info = lingodev.detect_language(text) if lingodev else {"language": "en"}
        detected_lang = language_info.get('language', 'en')
        print(f"   └─ Language: {detected_lang}")

        # Step 2: Translation to English if needed
        print("🌍 Translating text to English for standardized analysis...")
        source_lang = detected_lang

        if source_lang != 'en':
            try:
                translator = GoogleTranslator(source=source_lang, target='en')
                translated_text = translator.translate(text)
            except Exception as e:
                print(f"Translation failed: {e}. Using original text.")
                translated_text = text
        else:
            translated_text = text

        print(f"   └─ Translated text: {translated_text[:100]}...")

        # Step 3: Analyze with Gemini
        print("2️⃣ Analyzing with Gemini AI...")
        gemini_analysis = gemini_client.analyze_communication(translated_text, detected_lang)

        # Extract Gemini results
        emotion = gemini_analysis.get('emotion', 'neutral')
        ambiguity_score = gemini_analysis.get('ambiguity_score', 5.0)
        misunderstandings = gemini_analysis.get('misunderstandings', [])
        improved_version = gemini_analysis.get('improved_version', text)
        tone = gemini_analysis.get('tone', 'neutral')
        clarity_issues = gemini_analysis.get('clarity_issues', [])

        print(f"   └─ Primary emotion: {emotion}")
        print(f"   └─ Ambiguity score: {ambiguity_score}/10")
        print(f"   └─ Generated {len(misunderstandings)} misunderstanding scenarios")

        # Step 4: Cultural context (LingoDev)
        print("4️⃣ Getting cultural context...")
        cultural_context = lingodev.get_cultural_context(
            text=translated_text,
            source_lang=source_lang,
            emotions=[emotion]
        ) if lingodev else {"insights": ["Cultural analysis unavailable"]}

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
                'primary_emotion': emotion,
                'intensity': min(ambiguity_score, 10.0) / 2,
                'emotions': [emotion],
                'tone': tone,
                'clarity_issues': clarity_issues
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
        'gemini': False,
        'lingodev': False
    }

    # Test Gemini
    if gemini_client:
        try:
            test_result = gemini_client.analyze_communication("Hello world", "en")
            results['gemini'] = test_result.get('emotion') is not None
        except Exception as e:
            print(f"Gemini test failed: {e}")
            results['gemini'] = False

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
        'message': f"Gemini: {'✅' if results['gemini'] else '❌'}, LingoDev: {'✅' if results['lingodev'] else '❌'}"
    })


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'gemini_configured': gemini_client is not None,
        'lingodev_configured': lingodev is not None
    })


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🚀 The Misunderstanding Engine - Starting Server (Gemini Edition)")
    print("=" * 60)
    print(f"🌐 URL: http://127.0.0.1:5000")
    print(f"🧪 Test API: http://127.0.0.1:5000/test-api")
    print(f"💚 Health: http://127.0.0.1:5000/health")
    print("=" * 60 + "\n")
    print("\n" + "=" * 50)
    print("🔍 ENVIRONMENT VARIABLES CHECK:")
    print(f"GEMINI_API_KEY: {os.getenv('GEMINI_API_KEY')}")
    print(f"Key length: {len(os.getenv('GEMINI_API_KEY', ''))} characters")
    print(f"Starts with 'AIzaSy': {os.getenv('GEMINI_API_KEY', '').startswith('AIzaSy')}")
    print("=" * 50 + "\n")


    app.run(debug=True, port=5000)