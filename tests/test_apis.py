#!/usr/bin/env python3
"""Test all API connections (Weaviate, FriendliAI, OpenAI)."""

import os
import sys
import json
from dotenv import load_dotenv

def test_weaviate_connection():
    """Test Weaviate database connection."""
    print("🧪 Testing Weaviate connection...")
    
    try:
        from weaviate_client import get_client, ensure_schema
        
        # Test connection
        client = get_client()
        
        # Test if we can connect
        if client.is_ready():
            print("✅ Weaviate connection successful")
            
            # Test schema creation
            ensure_schema(client)
            print("✅ Weaviate schema ready")
            
            return True
        else:
            print("❌ Weaviate not ready")
            return False
            
    except Exception as e:
        print(f"❌ Weaviate connection failed: {e}")
        return False

def test_friendli_api():
    """Test FriendliAI API connection."""
    print("🧪 Testing FriendliAI API...")
    
    try:
        import requests
        
        # Get API credentials
        token = os.getenv("FRIENDLI_TOKEN") or os.getenv("FRIENDLI_API_KEY")
        team = os.getenv("FRIENDLI_TEAM")
        
        if not token:
            print("❌ No FriendliAI token found")
            return False
        
        # Test API call
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        if team:
            headers["X-Friendli-Team"] = team
        
        # Try to list models or get account info
        response = requests.get("https://api.friendli.ai/v1/models", headers=headers, timeout=10)
        
        if response.status_code == 200:
            models = response.json()
            print(f"✅ FriendliAI API working - Found {len(models.get('data', []))} models")
            return True
        elif response.status_code == 401:
            print("❌ FriendliAI authentication failed - check your token")
            return False
        else:
            print(f"❌ FriendliAI API error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ FriendliAI API test failed: {e}")
        return False

def test_openai_embeddings():
    """Test OpenAI embeddings API (used for Weaviate)."""
    print("🧪 Testing OpenAI embeddings API...")
    
    try:
        from openai import OpenAI
        
        # Try OpenAI first (more reliable for embeddings)
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("FRIENDLI_TOKEN") or os.getenv("FRIENDLI_API_KEY")
        
        if not api_key:
            print("❌ No API key found for embeddings")
            return False
        
        client = OpenAI(api_key=api_key)
        
        # Test embedding generation
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=["test embedding"]
        )
        
        if response.data and len(response.data) > 0:
            embedding_length = len(response.data[0].embedding)
            print(f"✅ Embeddings API working - Generated {embedding_length}D vector")
            return True
        else:
            print("❌ No embedding data returned")
            return False
            
    except Exception as e:
        print(f"❌ Embeddings API test failed: {e}")
        return False

def test_llm_generation():
    """Test LLM generation (FriendliAI with OpenAI fallback)."""
    print("🧪 Testing LLM generation...")
    
    try:
        from openai import OpenAI
        
        # Try OpenAI first (more reliable)
        openai_key = os.getenv("OPENAI_API_KEY")
        friendli_key = os.getenv("FRIENDLI_TOKEN") or os.getenv("FRIENDLI_API_KEY")
        
        if openai_key:
            print("🔄 Testing OpenAI...")
            try:
                client = OpenAI(api_key=openai_key)
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": "Say 'test successful' in JSON format"}],
                    response_format={"type": "json_object"},
                    max_tokens=50,
                    temperature=0.1
                )
                
                result = json.loads(response.choices[0].message.content)
                print(f"✅ OpenAI working - Response: {result}")
                return True
                
            except Exception as e:
                print(f"⚠️  OpenAI failed: {e}")
        
        # Fallback to FriendliAI
        if friendli_key:
            print("🔄 Testing FriendliAI fallback...")
            try:
                # Configure for FriendliAI
                client = OpenAI(
                    api_key=friendli_key,
                    base_url="https://api.friendli.ai/v1"
                )
                
                response = client.chat.completions.create(
                    model="meta-llama-3.1-8b-instruct",
                    messages=[{"role": "user", "content": "Say 'test successful' in JSON format"}],
                    response_format={"type": "json_object"},
                    max_tokens=50,
                    temperature=0.1
                )
                
                result = json.loads(response.choices[0].message.content)
                print(f"✅ FriendliAI fallback working - Response: {result}")
                return True
                
            except Exception as e:
                print(f"⚠️  FriendliAI fallback failed: {e}")
        
        print("❌ No working LLM API found")
        return False
        
    except Exception as e:
        print(f"❌ LLM generation test failed: {e}")
        return False

def main():
    """Run all API tests."""
    print("🚀 Testing All API Connections")
    print("=" * 40)
    
    # Load environment
    load_dotenv()
    
    # Run tests (skip FriendliAI since we're using OpenAI)
    results = {
        "Weaviate": test_weaviate_connection(),
        "Embeddings": test_openai_embeddings(),
        "LLM Generation": test_llm_generation()
    }
    
    print("\n📊 Test Results:")
    print("=" * 40)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:15} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 40)
    
    if all_passed:
        print("🎉 All API connections working!")
        print("✅ Ready to test the full bot workflow")
    else:
        print("⚠️  Some API connections failed")
        print("🔧 Check your .env file and API credentials")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)