#!/usr/bin/env python3

import requests
import json
import time

def check_backend_health():
    """Check if backend is healthy"""
    try:
        print("🔄 Checking backend health...")
        response = requests.get("https://ai-coding-51ss.onrender.com/api/health", timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend is healthy!")
            print(f"   Version: {data.get('version', 'unknown')}")
            print(f"   Status: {data.get('status')}")
            print(f"   EmergentIntegrations: {data.get('emergent_available')}")
            print(f"   Providers: {data.get('supported_providers')}")
            return True
        else:
            print(f"❌ Backend unhealthy: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend check failed: {e}")
        return False

def check_model_support():
    """Check if the corrected model is now supported"""
    try:
        print("\n🔄 Testing model support...")
        
        # Try to create a session with gpt-3.5-turbo
        payload = {
            "task": "Test task",
            "project_name": "TestProject", 
            "model_type": "gpt-3.5-turbo",
            "api_key": "sk-test-key-fake",
            "provider": "openai"
        }
        
        response = requests.post(
            "https://ai-coding-51ss.onrender.com/api/sessions",
            json=payload,
            timeout=15
        )
        
        print(f"   Response code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Model gpt-3.5-turbo is now supported!")
            return True
        elif "Unsupported model type" in response.text:
            print("❌ Model gpt-3.5-turbo still not supported")
            print(f"   Error: {response.text}")
            return False
        elif "Authentication" in response.text or "API key" in response.text:
            print("✅ Model gpt-3.5-turbo is supported (auth error expected with fake key)")
            return True
        else:
            print(f"⚠️  Unexpected response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False

def check_frontend():
    """Check if frontend is accessible"""
    try:
        print("\n🔄 Checking frontend...")
        response = requests.get("https://kodix.netlify.app/", timeout=10)
        
        if response.status_code == 200:
            print("✅ Frontend is accessible!")
            return True
        else:
            print(f"❌ Frontend issue: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend check failed: {e}")
        return False

def main():
    print("🔍 Checking current API status...\n")
    
    results = []
    results.append(check_backend_health())
    results.append(check_model_support())
    results.append(check_frontend())
    
    print(f"\n📊 Results: {sum(results)}/{len(results)} checks passed")
    
    if all(results):
        print("🎉 All systems are working! The fixes may already be deployed.")
    elif results[0]:  # Backend is healthy
        if not results[1]:  # But model issue persists
            print("⚠️  Backend is healthy but model fix not deployed yet.")
    else:
        print("❌ Backend has issues. Need to investigate.")
    
    return 0 if all(results) else 1

if __name__ == "__main__":
    main()