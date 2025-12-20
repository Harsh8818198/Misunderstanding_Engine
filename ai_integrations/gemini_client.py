"""
Gemini AI Client for LingoDev Communication Analysis
This replaces OpenRouter_client.py with Gemini API integration
"""

import os
import json
import google.generativeai as genai
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeminiClient:
    """Client for interacting with Google Gemini API"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini client

        Args:
            api_key: Gemini API key (if not provided, reads from environment)
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        # Configure Gemini
        genai.configure(api_key=self.api_key)

        # Initialize model - using gemini-pro for text generation
        # For production, consider gemini-1.5-pro or gemini-1.5-flash
        self.model_name = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
        self.model = genai.GenerativeModel(self.model_name)

        logger.info(f"Gemini client initialized with model: {self.model_name}")

    def analyze_communication(self, text: str, language: str = "en") -> Dict:
        """
        Analyze text for emotions, ambiguity, and communication improvements

        Args:
            text: The text to analyze
            language: Language code of the text

        Returns:
            Dictionary containing analysis results
        """
        try:
            prompt = self._build_analysis_prompt(text, language)

            # Generate response
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    top_p=0.9,
                    top_k=40,
                    max_output_tokens=2048,
                )
            )

            # Parse response
            result = self._parse_analysis_response(response.text)

            logger.info(f"Successfully analyzed text: {text[:50]}...")
            return result

        except Exception as e:
            logger.error(f"Error analyzing communication: {str(e)}")
            return self._get_fallback_response(text)

    def _build_analysis_prompt(self, text: str, language: str) -> str:
        """Build the prompt for communication analysis"""

        prompt = f"""You are an expert communication analyst. Analyze the following text and provide a detailed JSON response.

Text to analyze: "{text}"
Language: {language}

Provide your analysis in the following JSON format (respond ONLY with valid JSON, no markdown formatting):

{{
    "emotion": "primary emotion (e.g., happy, sad, angry, neutral, frustrated, excited)",
    "ambiguity_score": <number between 0-10, where 0 is clear and 10 is very ambiguous>,
    "misunderstandings": [
        "potential misunderstanding 1",
        "potential misunderstanding 2",
        "potential misunderstanding 3"
    ],
    "improved_version": "A clearer, more effective version of the message",
    "tone": "overall tone of the message",
    "clarity_issues": [
        "issue 1",
        "issue 2"
    ]
}}

Consider:
1. Emotional undertones and explicit emotions
2. Potential for misinterpretation
3. Ambiguous phrases or words
4. Cultural context
5. How the message could be clearer

Respond with ONLY the JSON object, no additional text."""

        return prompt

    def _parse_analysis_response(self, response_text: str) -> Dict:
        """Parse the Gemini response into structured data"""

        try:
            # Remove markdown code blocks if present
            cleaned_text = response_text.strip()
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.startswith('```'):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]

            cleaned_text = cleaned_text.strip()

            # Parse JSON
            result = json.loads(cleaned_text)

            # Validate and set defaults
            return {
                'emotion': result.get('emotion', 'neutral'),
                'ambiguity_score': float(result.get('ambiguity_score', 5.0)),
                'misunderstandings': result.get('misunderstandings', [
                    "Unable to determine specific misunderstandings"
                ]),
                'improved_version': result.get('improved_version',
                                               "Consider being more specific and direct in your communication."),
                'tone': result.get('tone', 'neutral'),
                'clarity_issues': result.get('clarity_issues', [])
            }

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response text: {response_text}")
            return self._get_fallback_response("")
        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            return self._get_fallback_response("")

    def _get_fallback_response(self, text: str) -> Dict:
        """Return a fallback response when analysis fails"""
        return {
            'emotion': 'neutral',
            'ambiguity_score': 5.0,
            'misunderstandings': [
                "Unable to analyze this text. Please try again."
            ],
            'improved_version': text if text else "Unable to provide improvement suggestions.",
            'tone': 'neutral',
            'clarity_issues': ['Analysis temporarily unavailable']
        }

    def generate_text(self, prompt: str, max_tokens: int = 1024) -> str:
        """
        Generate text based on a prompt

        Args:
            prompt: The input prompt
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text
        """
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.8,
                    max_output_tokens=max_tokens,
                )
            )
            return response.text

        except Exception as e:
            logger.error(f"Error generating text: {str(e)}")
            return "Unable to generate response."

    def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        Have a conversation with the model

        Args:
            messages: List of message dicts with 'role' and 'content'

        Returns:
            Model's response
        """
        try:
            # Convert messages to Gemini chat format
            chat = self.model.start_chat(history=[])

            # Build conversation
            for msg in messages[:-1]:  # All but last message
                if msg['role'] == 'user':
                    chat.send_message(msg['content'])

            # Send final message and get response
            response = chat.send_message(messages[-1]['content'])
            return response.text

        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            return "Unable to continue conversation."


# Convenience function for backward compatibility
def analyze_text(text: str, language: str = "en", api_key: Optional[str] = None) -> Dict:
    """
    Convenience function to analyze text

    Args:
        text: Text to analyze
        language: Language code
        api_key: Optional API key

    Returns:
        Analysis results
    """
    client = GeminiClient(api_key=api_key)
    return client.analyze_communication(text, language)


if __name__ == "__main__":
    # Test the client
    print("Testing Gemini Client...")

    # Example usage
    test_text = "I'm fine...."

    try:
        client = GeminiClient()
        result = client.analyze_communication(test_text)

        print("\nAnalysis Results:")
        print(json.dumps(result, indent=2))

    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure to set GEMINI_API_KEY environment variable")