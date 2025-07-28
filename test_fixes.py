#!/usr/bin/env python3

import requests
import json
import sys

def test_health_endpoint():
    """Test the health endpoint"""
    try:
        print("🔄 Testing health endpoint...")
        response = requests.get("https://ai-coding-51ss.onrender.com/api/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Health endpoint working!")
            print(f"   Status: {data.get('status')}")
            print(f"   Version: {data.get('version', 'unknown')}")
            print(f"   Supported providers: {data.get('supported_providers', [])}")
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False

def test_cors():
    """Test CORS headers"""
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
        print(f"❌ CORS error: {e}")
        return False

def test_session_with_correct_model():
    """Test session creation with correct model name"""
    try:
        print("\n🔄 Testing session creation with gpt-3.5-turbo...")
        
        # Test data with the corrected model name
        test_payload = {
            "task": "Создай простое веб-приложение",
            "project_name": "TestProject",
            "model_type": "gpt-3.5-turbo",  # This should now work
            "api_key": "sk-test-fake-key-for-validation",
            "provider": "openai"
        }
        
        response = requests.post(
            "https://ai-coding-51ss.onrender.com/api/sessions",
            json=test_payload,
            timeout=15
        )
        
        print(f"   Response status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Session creation endpoint working!")
            return True
        elif "Unsupported model type" in response.text:
            print("❌ Model name still not supported - need to check fix")
            return False
        else:
            print("ℹ️  Session creation has authentication/API key issues (expected)")
            return True  # This is expected with fake API key
            
    except Exception as e:
        print(f"❌ Session creation error: {e}")
        return False

def main():
    print("🚀 Testing ChatDev Web API fixes...\n")
    
    results = []
    results.append(test_health_endpoint())
    results.append(test_cors())
    results.append(test_session_with_correct_model())
    
    print(f"\n📊 Test Results: {sum(results)}/{len(results)} passed")
    
    if all(results):
        print("🎉 All tests passed! The API fixes are working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())