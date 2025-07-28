#!/usr/bin/env python3

import requests
import json

# Test the current state
OPENAI_API_KEY = "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"

print("🔍 QUICK DIAGNOSTIC TEST")
print("=" * 50)

# Test 1: Health check
print("\n1. Testing backend health...")
try:
    response = requests.get("https://ai-coding-51ss.onrender.com/api/health", timeout=10)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Version: {data.get('version', 'unknown')}")
        print(f"   Supported models: {data.get('supported_models', {})}")
    else:
        print(f"   Error: {response.text}")
except Exception as e:
    print(f"   Exception: {e}")

# Test 2: Frontend loading
print("\n2. Testing frontend loading...")
try:
    response = requests.get("https://kodix.netlify.app/", timeout=10)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
        print(f"   Size: {len(response.content)} bytes")
    else:
        print(f"   Error: {response.text}")
except Exception as e:
    print(f"   Exception: {e}")

# Test 3: Session creation with real API key
print("\n3. Testing session creation...")
try:
    payload = {
        "task": "Создай простую HTML страницу",
        "project_name": "TestProject",
        "model_type": "gpt-3.5-turbo",
        "api_key": OPENAI_API_KEY,
        "provider": "openai"
    }
    
    response = requests.post(
        "https://ai-coding-51ss.onrender.com/api/sessions",
        json=payload,
        timeout=20
    )
    
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text}")
    
    if response.status_code == 200:
        print("   ✅ SESSION CREATION WORKS!")
    else:
        print("   ❌ SESSION CREATION FAILED")
        
except Exception as e:
    print(f"   Exception: {e}")

# Test 4: Direct OpenAI test
print("\n4. Testing OpenAI API directly...")
try:
    import openai
    
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello"}],
        max_tokens=10
    )
    
    print(f"   ✅ OpenAI API works: {response.choices[0].message.content}")
    
except Exception as e:
    print(f"   ❌ OpenAI API error: {e}")

print("\n" + "=" * 50)
print("🎯 DIAGNOSTIC COMPLETE")