#!/usr/bin/env python3
"""Test LLM response format fix."""

import os
import sys
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from llm_client import generate_memo
from weaviate_client import build_context

def test_llm_response():
    """Test LLM response format with sample data."""
    print("🔄 Testing LLM response format...")
    
    # Sample context data
    sample_docs = [
        ("NVIDIA Corporation is a leading technology company that designs graphics processing units (GPUs) for gaming, professional visualization, data centers, and automotive markets. The company has become a dominant force in artificial intelligence computing.", 0.2, "NVIDIA Overview"),
        ("Recent financial performance shows strong growth in data center revenue, reaching $47.5B in fiscal 2024. Key products include GeForce gaming GPUs, professional Quadro cards, Tesla data center accelerators.", 0.3, "NVIDIA Financials"),
        ("The company faces competition from AMD and Intel but maintains technological leadership in high-performance computing. Recent developments include partnerships with major cloud providers.", 0.4, "NVIDIA Competition")
    ]
    
    context = build_context(sample_docs)
    
    try:
        # Test memo generation
        memo_content = generate_memo(
            name="NVIDIA",
            stage="Public",
            check_size="$10M",
            horizon="3 years",
            context=context
        )
        
        print("✅ LLM response generated")
        print(f"Response length: {len(memo_content)} characters")
        
        # Test JSON parsing
        try:
            data = json.loads(memo_content)
            print("✅ JSON parsing successful")
            
            # Validate required keys
            required_keys = ["verdict", "scores", "pros", "cons", "key_metrics", "biggest_risks", "fit_for_profile", "disclaimer"]
            missing_keys = [key for key in required_keys if key not in data]
            
            if missing_keys:
                print(f"❌ Missing keys: {missing_keys}")
                return False
            else:
                print("✅ All required keys present")
            
            # Validate scores structure
            if "scores" in data and isinstance(data["scores"], dict):
                score_keys = ["team", "problem", "market", "moat", "traction", "gtm", "unit_economics", "risks"]
                missing_score_keys = [key for key in score_keys if key not in data["scores"]]
                
                if missing_score_keys:
                    print(f"❌ Missing score keys: {missing_score_keys}")
                    return False
                else:
                    print("✅ All score keys present")
            
            # Show sample output
            print("\n📊 Sample Analysis:")
            print(f"Verdict: {data.get('verdict', 'N/A')}")
            print(f"Team Score: {data.get('scores', {}).get('team', 'N/A')}")
            print(f"Market Score: {data.get('scores', {}).get('market', 'N/A')}")
            print(f"First Pro: {data.get('pros', ['N/A'])[0] if data.get('pros') else 'N/A'}")
            print(f"First Con: {data.get('cons', ['N/A'])[0] if data.get('cons') else 'N/A'}")
            
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {e}")
            print(f"Raw response: {memo_content[:500]}...")
            return False
            
    except Exception as e:
        print(f"❌ LLM generation failed: {e}")
        return False

def main():
    """Run LLM fix test."""
    print("🚀 Testing LLM response format fix...\n")
    
    # Check required environment variables
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("FRIENDLI_API_KEY"):
        print("❌ Missing LLM API key (OPENAI_API_KEY or FRIENDLI_API_KEY)")
        return False
    
    success = test_llm_response()
    
    if success:
        print("\n🎉 LLM response format test passed!")
        print("✅ JSON structure is valid")
        print("✅ All required fields are present")
        print("✅ Ready for Discord bot integration")
    else:
        print("\n❌ LLM response format test failed")
        print("⚠️  Check the error messages above")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)