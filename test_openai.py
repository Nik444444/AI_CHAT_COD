#!/usr/bin/env python3

import sys
import openai

def test_openai_client():
    try:
        print(f"OpenAI version: {openai.__version__}")
        
        # Test client initialization
        client = openai.OpenAI(
            api_key="sk-test-key-not-real",
            timeout=30.0
        )
        print("OpenAI client initialized successfully")
        return True
        
    except Exception as e:
        print(f"Error initializing OpenAI client: {e}")
        return False

if __name__ == "__main__":
    test_openai_client()