"""
LingoDev API Integration
Multi-language support and cultural context analysis
"""

import os
import requests
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()


class LingoDevClient:
    """LingoDev API client for language detection and translation"""

    def __init__(self):
        self.api_key = os.getenv('LINGODEV_API_KEY')

        if not self.api_key:
            print("⚠️ LINGODEV_API_KEY not found. Language features will be limited.")

        # LingoDev API endpoint (adjust based on actual API documentation)
        self.base_url = "https://api.lingodev.ai/v1"  # Update with actual URL

        print("🌐 LingoDev initialized")

    def detect_language(self, text: str) -> Dict:
        """
        Detect the language of input text

        Args:
            text: Input text

        Returns:
            Dict with language info
        """
        # Mock implementation - replace with actual API call
        # Check LingoDev documentation for correct endpoint

        try:
            # Example API call structure:
            # response = requests.post(
            #     f"{self.base_url}/detect",
            #     headers={"Authorization": f"Bearer {self.api_key}"},
            #     json={"text": text}
            # )
            # return response.json()

            # Mock response for now
            return {
                "language": "en",
                "language_name": "English",
                "confidence": 0.95
            }

        except Exception as e:
            print(f"LingoDev Error (detect): {e}")
            return {
                "language": "en",
                "language_name": "English",
                "confidence": 0.5
            }

    def get_cultural_context(self, text, source_lang=None, target_lang="en", emotions=None):
        """
        Generate cultural interpretation insights between two languages.
        """
        try:
            # Example cultural data (you can extend this using cultural_multipliers folder)
            cultural_data = {
                "en": {"happiness": 0.6, "sadness": 0.7, "anger": 0.5},
                "pt": {"happiness": 0.8, "sadness": 0.6, "anger": 0.4},
                "ja": {"happiness": 0.4, "sadness": 0.8, "anger": 0.3}
            }

            insights = []
            if not emotions:
                emotions = ["neutral"]

            for emotion in emotions:
                s_val = cultural_data.get(source_lang, {}).get(emotion, 0.5)
                t_val = cultural_data.get(target_lang, {}).get(emotion, 0.5)
                diff = abs(s_val - t_val)

                if diff > 0.3:
                    description = (
                        f"In {target_lang.upper()} cultures, expressing '{emotion}' may feel "
                        f"{'more restrained' if s_val > t_val else 'more expressive'} "
                        f"than in {source_lang.upper()} cultures."
                    )
                    insights.append(description)

            if not insights:
                insights.append("Minimal cultural interpretation differences detected.")

            return {
                "insights": insights,
                "cultural_distance_score": round(sum(abs(
                    cultural_data.get(source_lang, {}).get(e, 0.5) -
                    cultural_data.get(target_lang, {}).get(e, 0.5)
                ) for e in emotions) / len(emotions), 2)
            }

        except Exception as e:
            print(f"LingoDev Error (get_cultural_context): {e}")
            return {"insights": ["Cultural analysis unavailable."]}

    def translate_with_context(self, text: str, target_lang: str = "en") -> Optional[str]:
        """
        Translate text with cultural context preservation
        (placeholder for contextual translation logic)
        """
        try:
            # Mock implementation
            return text
        except Exception as e:
            print(f"LingoDev Error (translate_with_context): {e}")
            return None

    def translate_text(self, text: str, source_lang: str = None, target_lang: str = "en") -> Optional[str]:
        """
        Translate text from source to target language using LingoDev API.
        """
        try:
            payload = {
                "text": text,
                "source_lang": source_lang,
                "target_lang": target_lang
            }
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.post(f"{self.base_url}/translate", json=payload, headers=headers)
            response.raise_for_status()
            return response.json().get("translation", text)

        except Exception as e:
            print(f"LingoDev Error (translate_text): {e}")
            return text


# Test function
if __name__ == "__main__":
    print("Testing LingoDev Integration...")

    client = LingoDevClient()
    test_text = "I'm fine with whatever."

    language = client.detect_language(test_text)
    print(f"✅ Language detected: {language}")

    context = client.get_cultural_context(test_text)
    print(f"✅ Cultural context: {context}")