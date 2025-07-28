#!/usr/bin/env python3

import requests
import json
import time

# Real OpenAI API key provided by user
OPENAI_API_KEY = "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"

def test_backend_health():
    """Test backend health endpoint"""
    try:
        print("🔄 Testing backend health...")
        response = requests.get("https://ai-coding-51ss.onrender.com/api/health", timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend health check passed!")
            print(f"   Status: {data.get('status')}")
            print(f"   Version: {data.get('version', 'unknown')}")
            print(f"   Emergent available: {data.get('emergent_available')}")
            print(f"   Supported providers: {data.get('supported_providers')}")
            return True, data
        else:
            print(f"❌ Backend health failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False, None
    except Exception as e:
        print(f"❌ Backend health error: {e}")
        return False, None

def test_cors():
    """Test CORS endpoint"""
    try:
        print("\n🔄 Testing CORS...")
        response = requests.get(
            "https://ai-coding-51ss.onrender.com/api/cors-test",
            headers={"Origin": "https://kodix.netlify.app"},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ CORS test passed!")
            return True
        else:
            print(f"❌ CORS test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ CORS test error: {e}")
        return False

def test_session_creation():
    """Test session creation with real API key"""
    try:
        print("\n🔄 Testing session creation with REAL API key...")
        
        payload = {
            "task": "Создай простой калькулятор на HTML и JavaScript",
            "project_name": "TestCalculator",
            "model_type": "gpt-3.5-turbo",
            "api_key": OPENAI_API_KEY,
            "provider": "openai"
        }
        
        response = requests.post(
            "https://ai-coding-51ss.onrender.com/api/sessions",
            json=payload,
            timeout=30
        )
        
        print(f"   Response status: {response.status_code}")
        print(f"   Response body: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Session creation successful!")
            print(f"   Session ID: {data.get('session_id')}")
            return True, data.get('session_id')
        else:
            print(f"❌ Session creation failed: {response.status_code}")
            return False, None
            
    except Exception as e:
        print(f"❌ Session creation error: {e}")
        return False, None

def test_direct_openai():
    """Test OpenAI API directly to ensure key works"""
    try:
        print("\n🔄 Testing OpenAI API directly...")
        
        import openai
        
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello, this is a test"}],
            max_tokens=50
        )
        
        print("✅ Direct OpenAI API test passed!")
        print(f"   Response: {response.choices[0].message.content[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ Direct OpenAI API test failed: {e}")
        return False

def test_frontend_loading():
    """Test if frontend loads"""
    try:
        print("\n🔄 Testing frontend loading...")
        
        response = requests.get("https://kodix.netlify.app/", timeout=10)
        
        if response.status_code == 200:
            print("✅ Frontend loads successfully!")
            print(f"   Content length: {len(response.text)} chars")
            
            # Check if it contains React app indicators
            if "react" in response.text.lower() or "vite" in response.text.lower():
                print("   ℹ️  Detected React/Vite app")
            
            return True
        else:
            print(f"❌ Frontend loading failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Frontend loading error: {e}")
        return False

def main():
    print("🚀 Starting comprehensive testing with REAL API key...\n")
    
    results = {}
    
    # Test backend health
    results['health'], health_data = test_backend_health()
    
    # Test CORS
    results['cors'] = test_cors()
    
    # Test direct OpenAI API
    results['openai_direct'] = test_direct_openai()
    
    # Test session creation
    results['session'], session_id = test_session_creation()
    
    # Test frontend
    results['frontend'] = test_frontend_loading()
    
    print(f"\n📊 Test Results:")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    print(f"\nOverall: {sum(results.values())}/{len(results)} tests passed")
    
    if not all(results.values()):
        print("\n❌ Some tests failed. Issues identified:")
        
        if not results['health']:
            print("   - Backend health check failed")
        if not results['cors']:
            print("   - CORS configuration issues")
        if not results['openai_direct']:
            print("   - OpenAI API key or connection issues")
        if not results['session']:
            print("   - Session creation failed")
        if not results['frontend']:
            print("   - Frontend loading issues")
    else:
        print("\n🎉 All tests passed! The system should be working.")

if __name__ == "__main__":
    main()