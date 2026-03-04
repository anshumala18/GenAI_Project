#!/usr/bin/env python3
"""List available xAI Grok models"""

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key or not api_key.startswith("xai-"):
    print("❌ xAI API key not found")
    exit(1)

print("Connecting to xAI API...")
client = OpenAI(
    api_key=api_key,
    base_url="https://api.x.ai/v1",
)

try:
    print("\nFetching available models...")
    models = client.models.list()
    
    print("\n✅ Available models:")
    for model in models.data:
        print(f"  • {model.id}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nTrying common model names instead...")
    
    # Try common xAI model names
    common_models = [
        "grok-2-latest",
        "grok-latest", 
        "grok-vision-beta",
        "grok-2-vision-beta",
        "grok",
        "grok-2",
    ]
    
    for model_name in common_models:
        try:
            print(f"\nTesting model: {model_name}...", end=" ")
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=10,
            )
            print(f"✅ WORKS!")
            break
        except Exception as err:
            if "not found" in str(err).lower():
                print("❌ Not found")
            else:
                print(f"❓ Error: {err}")
