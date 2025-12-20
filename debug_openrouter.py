"""
Debug script to test OpenRouter API key
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()


def test_api_key():
    api_key = os.getenv('OPENROUTER_API_KEY')

    print("=" * 60)
    print("🔧 OpenRouter API Key Debugger")
    print("=" * 60)

    # Check if key exists
    if not api_key:
        print("❌ ERROR: No API key found in .env file!")
        print("   Add this to your .env file:")
        print("   OPENROUTER_API_KEY=sk-or-v1-your-key-here")
        return

    print(f"✅ API key found: {api_key[:20]}...{api_key[-4:]}")
    print(f"   Length: {len(api_key)} characters")

    # Check format
    if not api_key.startswith('sk-or-v1-'):
        print("⚠️  WARNING: Key doesn't start with 'sk-or-v1-'")
        print("   This might be an old or invalid key format")

    # Test 1: Simple API call with minimal model
    print("\n" + "=" * 60)
    print("🧪 Test 1: Testing with free model (meta-llama/llama-3.2-3b-instruct:free)")
    print("=" * 60)

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "Misunderstanding-Engine",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "meta-llama/llama-3.2-3b-instruct:free",  # Free model for testing
        "messages": [
            {"role": "user", "content": "Reply with just the word 'hello'"}
        ],
        "max_tokens": 10
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            print("✅ SUCCESS! Your API key works!")
            data = response.json()
            reply = data.get('choices', [{}])[0].get('message', {}).get('content', 'No response')
            print(f"Response: {reply}")

            # Now test with Claude
            print("\n" + "=" * 60)
            print("🧪 Test 2: Testing with Claude 3.5 Haiku")
            print("=" * 60)

            payload['model'] = "anthropic/claude-3.5-haiku"
            response2 = requests.post(url, headers=headers, json=payload, timeout=15)

            print(f"Status Code: {response2.status_code}")

            if response2.status_code == 200:
                print("✅ SUCCESS! Claude 3.5 Haiku works!")
                data2 = response2.json()
                reply2 = data2.get('choices', [{}])[0].get('message', {}).get('content', 'No response')
                print(f"Response: {reply2}")
            else:
                print(f"❌ Claude test failed: {response2.json()}")
                print("\n💡 Try these alternative models in your code:")
                print("   - meta-llama/llama-3.2-3b-instruct:free (free)")
                print("   - openai/gpt-3.5-turbo")
                print("   - anthropic/claude-3-haiku")

        else:
            print(f"❌ FAILED: {response.json()}")
            error_msg = response.json().get('error', {}).get('message', 'Unknown error')

            if 'User not found' in error_msg or response.status_code == 401:
                print("\n🔍 Diagnosis: Invalid or Expired API Key")
                print("\n📝 Steps to fix:")
                print("1. Go to https://openrouter.ai/")
                print("2. Sign in to your account")
                print("3. Go to Settings → API Keys")
                print("4. Generate a NEW API key")
                print("5. Replace the key in your .env file")
                print("6. Make sure there are NO spaces or quotes around the key")
                print("\n💡 Your .env should look like:")
                print("OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxx")
            elif response.status_code == 402:
                print("\n🔍 Diagnosis: Insufficient Credits")
                print("You need to add credits to your OpenRouter account")
                print("Visit: https://openrouter.ai/settings/billing")

    except requests.exceptions.Timeout:
        print("❌ Request timed out")
    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n" + "=" * 60)
    print("💡 Additional Checks:")
    print("=" * 60)
    print("1. Visit https://openrouter.ai/settings/keys")
    print("2. Check if your key is still active")
    print("3. Check your credit balance: https://openrouter.ai/settings/billing")
    print("4. Make sure you're logged into the correct account")
    print("=" * 60)


if __name__ == "__main__":
    test_api_key()