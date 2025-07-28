import requests
import json

def test_api():
    # Test health endpoint
    try:
        response = requests.get("https://ai-coding-51ss.onrender.com/api/health", timeout=10)
        print(f"Health check: {response.status_code}")
        print(f"Response: {response.json()}")
        return True
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_session_creation():
    # Test session creation
    try:
        payload = {
            "task": "Создай простое приложение",
            "project_name": "TestApp",
            "model_type": "gpt-3.5-turbo",
            "api_key": "sk-test-fake-key-for-testing",
            "provider": "openai"
        }
        
        response = requests.post(
            "https://ai-coding-51ss.onrender.com/api/sessions",
            json=payload,
            timeout=10
        )
        
        print(f"Session creation: {response.status_code}")
        print(f"Response: {response.text}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Session creation failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing API endpoints...")
    
    if test_api():
        print("✓ Health check passed")
    else:
        print("✗ Health check failed")
    
    if test_session_creation():
        print("✓ Session creation passed")
    else:
        print("✗ Session creation failed")