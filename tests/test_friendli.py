#!/usr/bin/env python3
"""Test FriendliAI API specifically."""

import os
import requests
import json
from dotenv import load_dotenv

def test_friendli_endpoints():
    """Test different FriendliAI endpoints to find the right one."""
    load_dotenv()
    
    token = os.getenv("FRIENDLI_TOKEN") or os.getenv("FRIENDLI_API_KEY")
    team = os.getenv("FRIENDLI_TEAM")
    
    if not token:
        print("❌ No FriendliAI token found")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    if team:
        headers["X-Friendli-Team"] = team
    
    # Test different endpoints
    endpoints = [
        "https://api.friendli.ai/v1/models",
        "https://api.friendli.ai/models",
        "https://api.friendli.ai/v1/endpoints",
        "https://api.friendli.ai/endpoints",
        "https://api.friendli.ai/v1/chat/completions",
    ]
    
    print("🧪 Testing FriendliAI endpoints...")
    
    for endpoint in endpoints:
        try:
            print(f"🔄 Testing: {endpoint}")
            response = requests.get(endpoint, headers=headers, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Success: {json.dumps(data, indent=2)[:200]}...")
                return True
            elif response.status_code == 405:  # Method not allowed - might need POST
                print(f"   ⚠️  Method not allowed - trying POST...")
                if "chat/completions" in endpoint:
                    # Try a simple chat completion
                    test_payload = {
                        "model": "meta-llama-3.1-8b-instruct",
                        "messages": [{"role": "user", "content": "Hello"}],
                        "max_tokens": 10
                    }
                    post_response = requests.post(endpoint, headers=headers, json=test_payload, timeout=10)
                    print(f"   POST Status: {post_response.status_code}")
                    if post_response.status_code == 200:
                        print(f"   ✅ POST Success!")
                        return True
                    else:
                        print(f"   POST Error: {post_response.text[:200]}")
            else:
                print(f"   Error: {response.text[:200]}")
                
        except Exception as e:
            print(f"   Exception: {e}")
    
    return False

def test_friendli_with_different_models():
    """Test FriendliAI with different model names."""
    load_dotenv()
    
    token = os.getenv("FRIENDLI_TOKEN") or os.getenv("FRIENDLI_API_KEY")
    team = os.getenv("FRIENDLI_TEAM")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    if team:
        headers["X-Friendli-Team"] = team
    
    # Try different model names
    models = [
        "meta-llama-3.1-8b-instruct",
        "llama-3.1-8b-instruct",
        "meta-llama-3-8b-instruct",
        "gpt-3.5-turbo",  # Sometimes they support OpenAI-compatible names
    ]
    
    endpoint = "https://api.friendli.ai/v1/chat/completions"
    
    print("🧪 Testing FriendliAI models...")
    
    for model in models:
        try:
            print(f"🔄 Testing model: {model}")
            
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": "Say hello"}],
                "max_tokens": 10,
                "temperature": 0.1
            }
            
            response = requests.post(endpoint, headers=headers, json=payload, timeout=15)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Success with {model}!")
                print(f"   Response: {data.get('choices', [{}])[0].get('message', {}).get('content', 'No content')}")
                return model
            else:
                print(f"   Error: {response.text[:200]}")
                
        except Exception as e:
            print(f"   Exception: {e}")
    
    return None

if __name__ == "__main__":
    print("🚀 FriendliAI API Testing")
    print("=" * 30)
    
    # Test endpoints
    endpoint_success = test_friendli_endpoints()
    
    if not endpoint_success:
        print("\n🔄 Testing specific models...")
        working_model = test_friendli_with_different_models()
        
        if working_model:
            print(f"\n✅ Found working model: {working_model}")
        else:
            print("\n❌ No working FriendliAI configuration found")
            print("💡 Suggestions:")
            print("1. Check if your token is correct")
            print("2. Check if your team ID is correct")
            print("3. Try using OpenAI API key as fallback")
    else:
        print("\n✅ FriendliAI API is working!")