#!/usr/bin/env python3
"""Test the complete workflow that was failing."""

import os
import sys
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from weaviate_client import (
    get_client,
    chunk_text,
    embed_chunks,
    upsert_chunks,
    query_company,
    calculate_confidence,
    build_context
)
from llm_client import generate_memo

def test_nvidia_workflow():
    """Test the complete NVIDIA workflow that was failing."""
    print("🔄 Testing complete NVIDIA workflow...")
    
    # NVIDIA data (similar to what user would input)
    nvidia_text = """
    NVIDIA Corporation is a leading technology company that designs graphics processing units (GPUs) for gaming, professional visualization, data centers, and automotive markets. The company has become a dominant force in artificial intelligence computing, with their GPUs powering machine learning and AI applications across industries. Recent financial performance shows strong growth in data center revenue, reaching $47.5B in fiscal 2024. Key products include GeForce gaming GPUs, professional Quadro cards, Tesla data center accelerators, and the CUDA parallel computing platform. The company faces competition from AMD and Intel but maintains technological leadership in high-performance computing. Recent developments include partnerships with major cloud providers and automotive manufacturers for autonomous vehicle technology. NVIDIA's market capitalization has grown significantly due to AI boom, with strong demand for their H100 and A100 chips for training large language models. The company has a strong moat through CUDA ecosystem and software stack that creates switching costs for customers.
    """
    
    try:
        # Step 1: Ingestion (simulate /ingest_company command)
        print("📥 Step 1: Ingesting NVIDIA data...")
        client = get_client()
        chunks = chunk_text(nvidia_text)
        print(f"Created {len(chunks)} chunks for NVIDIA")
        
        vectors = embed_chunks(chunks)
        print(f"Generated embeddings for {len(vectors)} chunks")
        
        chunk_count = upsert_chunks(client, "NVIDIA", "NVIDIA", "https://nvidia.com", chunks, vectors)
        print(f"✅ Inserted {chunk_count} chunks for NVIDIA")
        
        # Step 2: Retrieval and confidence check (simulate /vc_decide command)
        print("\n🔍 Step 2: Retrieving and checking confidence...")
        docs = query_company(client, "NVIDIA", k=5)
        print(f"Retrieved {len(docs)} documents")
        
        if not docs:
            print("❌ No documents retrieved")
            client.close()
            return False
        
        avg_similarity, is_confident = calculate_confidence(docs, threshold=0.25)
        print(f"Confidence: {avg_similarity:.3f} ({'✅ CONFIDENT' if is_confident else '❌ NOT CONFIDENT'})")
        
        if not is_confident:
            print(f"❌ Not enough evidence. Confidence: {avg_similarity:.3f} (threshold: 0.25)")
            client.close()
            return False
        
        # Step 3: Build context
        print("\n📄 Step 3: Building context...")
        context = build_context(docs)
        print(f"Context length: {len(context)} characters")
        print(f"Context preview: {context[:200]}...")
        
        # Step 4: Generate memo (this was failing before)
        print("\n🤖 Step 4: Generating VC memo...")
        memo_content = generate_memo("NVIDIA", "Public", "$10M", "3 years", context)
        
        # Step 5: Parse JSON (this was the main failure point)
        print("\n📊 Step 5: Parsing memo JSON...")
        try:
            data = json.loads(memo_content)
            print("✅ JSON parsing successful")
            
            # Display results like Discord would
            print("\n" + "="*50)
            print("NVIDIA INVESTMENT MEMO")
            print("="*50)
            print(f"🎯 Verdict: {data.get('verdict', 'N/A')}")
            
            scores = data.get('scores', {})
            print(f"\n📈 Scorecard:")
            for key, value in scores.items():
                print(f"  {key.replace('_', ' ').title()}: {value}/5")
            
            print(f"\n✅ Pros:")
            for pro in data.get('pros', []):
                print(f"  • {pro}")
            
            print(f"\n❌ Cons:")
            for con in data.get('cons', []):
                print(f"  • {con}")
            
            print(f"\n📊 Key Metrics:")
            for metric in data.get('key_metrics', []):
                print(f"  • {metric}")
            
            print(f"\n⚠️ Biggest Risks:")
            for risk in data.get('biggest_risks', []):
                print(f"  • {risk}")
            
            print(f"\n🎯 Fit for Profile: {data.get('fit_for_profile', 'N/A')}")
            print(f"\n⚖️ Disclaimer: {data.get('disclaimer', 'N/A')}")
            
            client.close()
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {e}")
            print(f"Raw response: {memo_content}")
            client.close()
            return False
            
    except Exception as e:
        print(f"❌ Workflow failed: {e}")
        try:
            client.close()
        except:
            pass
        return False

def main():
    """Run the complete workflow test."""
    print("🚀 Testing complete NVIDIA workflow (the one that was failing)...\n")
    
    # Check required environment variables
    required_vars = ["WEAVIATE_URL"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("FRIENDLI_API_KEY"):
        print("❌ Missing LLM API key (OPENAI_API_KEY or FRIENDLI_API_KEY)")
        return False
    
    success = test_nvidia_workflow()
    
    if success:
        print("\n🎉 Complete workflow test PASSED!")
        print("✅ The NVIDIA analysis issue has been fixed")
        print("✅ JSON parsing is working correctly")
        print("✅ Discord bot should now work properly")
        print("\n💡 You can now try the Discord commands again:")
        print("   1. /ingest_company name:NVIDIA link:https://nvidia.com text:[your NVIDIA description]")
        print("   2. /vc_decide name:NVIDIA stage:Public check_size:$10M horizon:3 years")
    else:
        print("\n❌ Workflow test FAILED")
        print("⚠️  There are still issues that need to be resolved")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)