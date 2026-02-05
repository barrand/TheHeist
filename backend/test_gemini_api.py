#!/usr/bin/env python3
"""
Quick test script to verify Gemini API models and endpoints
"""
import requests
import json
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv('/Users/bbarrand/Documents/Projects/TheHeist/.env')
API_KEY = os.getenv('GEMINI_API_KEY')

if not API_KEY:
    print("ERROR: GEMINI_API_KEY not found in .env file")
    exit(1)

print(f"API Key loaded: {API_KEY[:20]}...")

print("=" * 60)
print("GEMINI API TEST")
print("=" * 60)
print()

# Test 1: List available models
print("1. Testing: List available models...")
list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
try:
    response = requests.get(list_url)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        models = [m['name'] for m in data.get('models', [])]
        print(f"   ✅ Found {len(models)} models:")
        for model in models[:10]:  # Show first 10
            # Extract just the model name part
            model_name = model.split('/')[-1]
            print(f"      - {model_name}")
    else:
        print(f"   ❌ Error: {response.text}")
except Exception as e:
    print(f"   ❌ Exception: {e}")

print()

# Test 2: Try different model formats
test_models = [
    "gemini-1.5-flash",
    "gemini-1.5-flash-latest",
    "gemini-1.5-pro",
    "gemini-2.0-flash-exp",
]

print("2. Testing: Generate content with different models...")
for model in test_models:
    # Try with /models/ prefix
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={API_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{
                "text": "Say hello in one word."
            }]
        }]
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            result = response.json()
            text = result['candidates'][0]['content']['parts'][0]['text']
            print(f"   ✅ {model}: {text.strip()}")
        else:
            print(f"   ❌ {model}: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ {model}: {str(e)[:50]}")

print()
print("=" * 60)
print("Test complete!")
print("=" * 60)
