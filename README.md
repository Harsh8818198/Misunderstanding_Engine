# LingoDev - AI-Powered Communication Analysis

An intelligent communication analysis platform that detects emotions, analyzes ambiguity, and suggests improvements to help users communicate more clearly and effectively.

## 🌟 Features

- **Language Detection**: Automatically detects the language of input text
- **Emotion Analysis**: Identifies primary emotions in communication
- **Ambiguity Scoring**: Calculates potential misunderstanding levels (0-10 scale)
- **Misunderstanding Scenarios**: Generates possible misinterpretations
- **Communication Improvement**: Suggests clearer, more effective versions of messages
- **Multi-language Support**: Translates text for standardized analysis

## 🚀 Tech Stack

- **Backend**: Flask (Python)
- **AI/ML**: 
  - TensorFlow 2.20.0
  - Transformers 4.40.0
  - OpenRouter API (Claude 3.5 Haiku)
- **Translation**: Deep-translator
- **Language Detection**: langdetect
- **Server**: Gunicorn
- **Deployment**: Railway

## 📋 Prerequisites

- Python 3.8+
- OpenRouter API Key (for AI analysis)
- LingoDev API Key (optional, for enhanced features)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/lingodev.git
cd lingodev
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Activate on Linux/Mac
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the root directory:

```env
OPENROUTER_API_KEY=sk-or-v1-your-key-here
LINGODEV_API_KEY=your-lingodev-key-here  # Optional
PORT=8080
```

## 🏃 Running Locally

### Development Mode

```bash
python app.py
```

The application will be available at `http://localhost:8080`

### Production Mode (with Gunicorn)

```bash
gunicorn app:app --bind 0.0.0.0:8080
```

## 🐳 Docker Deployment

### Build Docker Image

```bash
docker build -t lingodev .
```

### Run Container

```bash
docker run -p 8080:8080 \
  -e OPENROUTER_API_KEY=your-key \
  lingodev
```

## ☁️ Deploying to Railway

### Method 1: Connect GitHub Repository

1. Push your code to GitHub
2. Go to [Railway.app](https://railway.app)
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Add environment variables in Railway dashboard
6. Deploy!

### Method 2: Railway CLI

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Add environment variables
railway variables set OPENROUTER_API_KEY=your-key

# Deploy
railway up
```

### Required Railway Environment Variables

```
OPENROUTER_API_KEY=sk-or-v1-xxxxx
LINGODEV_API_KEY=xxxxx  # Optional
PORT=8080  # Auto-set by Railway
```

## 📡 API Endpoints

### Analyze Text

**POST** `/analyze`

```json
{
  "text": "I'm fine...."
}
```

**Response:**

```json
{
  "original_text": "I'm fine....",
  "language": "en",
  "translated_text": "I'm fine....",
  "emotion": "neutral",
  "ambiguity_score": 5.0,
  "misunderstandings": [
    "Could be interpreted as..."
  ],
  "improved_version": "I'm doing well, thanks for asking!"
}
```

### Health Check

**GET** `/health`

```json
{
  "status": "healthy",
  "timestamp": "2025-11-15T16:44:26"
}
```

## 🔧 Configuration

### OpenRouter Model Configuration

The default model is `anthropic/claude-3.5-haiku`. To change it, modify in your code:

```python
OPENROUTER_MODEL = "anthropic/claude-3.5-haiku"  # or any other supported model
```

### Supported OpenRouter Models

- `anthropic/claude-3.5-haiku` (Fast, efficient)
- `anthropic/claude-3.5-sonnet` (Balanced)
- `anthropic/claude-opus` (Most capable)
- `openai/gpt-4` (Alternative)

## 🐛 Troubleshooting

### Error: "User not found" (401)

**Problem**: Invalid OpenRouter API key

**Solution**: 
1. Get a valid key from [OpenRouter.ai](https://openrouter.ai/)
2. Update environment variable: `OPENROUTER_API_KEY`
3. Redeploy your application

### Error: "LINGODEV_API_KEY not found"

**Problem**: Optional LingoDev key missing

**Solution**: This is a warning, not an error. The app will work with limited features. Add the key to unlock full functionality.

### TensorFlow GPU Warning

**Problem**: "Could not find cuda drivers"

**Solution**: This is expected on Railway/Docker. The app runs on CPU, which is sufficient for most use cases.

## 📁 Project Structure

```
lingodev/
├── .venv/                          # Virtual environment
├── ai_integrations/                # AI service clients
│   ├── __init__.py
│   ├── language_detector.py       # Language detection logic
│   ├── LingoDev_client.py         # LingoDev API integration
│   ├── OpenRouter_client.py       # OpenRouter/Claude integration
│   └── translator_client.py       # Translation service wrapper
├── data/                           # Data files
│   ├── cultural_multipliers       # Cultural context data
│   └── demo_examples              # Example inputs/outputs
├── routes/                         # Flask route handlers
│   ├── __init__.py
│   └── translator_routes.py       # Translation & analysis endpoints
├── src/                            # Core business logic
│   ├── auto_translate.py          # Automatic translation pipeline
│   ├── lingo_integration.py       # LingoDev service integration
│   ├── model_inference.py         # ML model inference
│   ├── translation_pipeline.py    # Full translation workflow
│   └── utils.py                   # Utility functions
├── static/                         # Static assets (CSS, JS, images)
├── templates/                      # HTML templates
│   ├── analysis.html              # Analysis results page
│   ├── index.html                 # Home page
│   └── translator.html            # Translation interface
├── .env                            # Environment variables (local)
├── app.py                          # Main Flask application
├── config.py                       # Configuration settings
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Docker configuration
├── railway.json                    # Railway deployment config
└── README.md                       # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Documentation**: [Your Docs URL]
- **OpenRouter**: [https://openrouter.ai/](https://openrouter.ai/)
- **Railway**: [https://railway.app/](https://railway.app/)
- **Support**: [Your Support Email/Link]

## ⚡ Performance

- **Average Response Time**: ~2-5 seconds
- **Supported Languages**: 50+ languages via deep-translator
- **Concurrent Requests**: Handles multiple simultaneous analyses
- **Uptime**: 99.9% on Railway infrastructure

## 🎯 Roadmap

- [ ] Add sentiment intensity analysis
- [ ] Support for audio/voice message analysis
- [ ] Real-time chat integration
- [ ] Multi-turn conversation context
- [ ] Custom emotion categories
- [ ] API rate limiting
- [ ] User authentication
- [ ] Analytics dashboard

## 📧 Contact

For questions or support, reach out to:
- **Email**: bhattharsh328@gmail.com
- **GitHub Issues**: [github.com/Harsh8818198/Misunderstanding_Engine/issues](github.com/Harsh8818198/Misunderstanding_Engine/issues)

---

Made with ❤️ by Harsh and Sahil
