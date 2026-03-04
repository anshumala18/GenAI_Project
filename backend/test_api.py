#!/usr/bin/env python3
"""Test script to verify Grok API is working correctly"""

import os
import json
import sys
from dotenv import load_dotenv
from openai import OpenAI
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

print("=" * 60)
print("GROK API TEST SCRIPT")
print("=" * 60)

if not api_key:
    print("❌ ERROR: GROQ_API_KEY not found in .env file")
    sys.exit(1)

print(f"✓ API Key found: {api_key[:15]}...{api_key[-15:]}")
print(f"✓ Key type: {'xAI' if api_key.startswith('xai-') else 'Groq'}")

# Initialize client
try:
    if api_key.startswith("xai-"):
        print("\n🔧 Initializing xAI client...")
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.x.ai/v1",
        )
        model = "grok-2-latest"
    else:
        print("\n🔧 Initializing Groq client...")
        client = Groq(api_key=api_key)
        model = "mixtral-8x7b-32768"
    
    print(f"✓ Client initialized for model: {model}")
except Exception as e:
    print(f"❌ Failed to initialize client: {e}")
    sys.exit(1)

# Test simple query
test_prompt = """Respond with ONLY a valid JSON object, no markdown or extra text.

{
  "test": "success",
  "message": "API is working"
}"""

print(f"\n🧪 Sending test request to {model}...")
response = None

# Use appropriate models based on API type
if "xai" in api_key.lower():
    # xAI Grok models
    possible_models = [
        "grok-2-latest",
        "grok-2-vision-beta",
        "grok-vision-latest",
        "grok-vision",
        "grok-beta",
        "grok-2",
        "grok-latest",
        "grok",
    ]
else:
    # Groq API models - use actual available models
    possible_models = [
        "mixtral-8x7b-32768",      # Fast & capable
        "llama-3.1-70b-versatile",  # Larger model
        "llama-3.1-8b-instant",     # Faster, smaller
        "llama-2-70b-chat",
        "gemma-7b-it",
    ]

print(f"Trying {len(possible_models)} possible models...")
for attempt_model in possible_models:
    try:
        print(f"  Trying {attempt_model}...", end=" ")
        response = client.chat.completions.create(
            model=attempt_model,
            messages=[
                {"role": "user", "content": test_prompt}
            ],
            temperature=0.1,
            max_tokens=500,
        )
        model = attempt_model
        print(f"✅ WORKS!")
        break
    except Exception as e:
        error_msg = str(e)
        if "not found" in error_msg.lower() or "model" in error_msg.lower():
            print(f"❌ Not found")
        else:
            print(f"❓ Error: {error_msg[:50]}")
        continue

if response is None:
    print("\n" + "=" * 60)
    if "xai" in api_key.lower():
        print("❌ CRITICAL: No xAI Grok model is available!")
        print("=" * 60)
        print("\nPossible causes:")
        print("1. Your xAI API key may not have access to Grok yet")
        print("2. The API key might be expired or revoked")
        print("\nNote: Use Groq API instead (faster & always works)")
    else:
        print("❌ CRITICAL: No Groq models are working!")
        print("=" * 60)
        print("\nPossible causes:")
        print("1. API key is invalid or expired")
        print("2. Account doesn't have API access")
        print("\nFix:")
        print("1. Visit: https://console.groq.com/settings/security")
        print("2. Delete old keys and create a new one")
        print("3. Update .env with the new key")
        print("4. Run test again")
    sys.exit(1)

content = response.choices[0].message.content.strip()
print(f"\n✓ Response received ({len(content)} chars):")
print(f"   {content[:100]}...")

# Try to parse JSON
if content.startswith("```"):
    content = content.split("```")[1]
    if content.startswith("json"):
        content = content[4:]
    content = content.strip()

try:
    result = json.loads(content)
    print(f"\n✅ API IS WORKING! JSON parsed successfully:")
    print(json.dumps(result, indent=2))
    
except json.JSONDecodeError as e:
    print(f"\n⚠️  JSON Parse Error: {e}")
    print(f"Raw response:\n{content}")
except Exception as e:
    print(f"\n❌ API Call Failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ TEST PASSED - API is functional")
print("=" * 60)
