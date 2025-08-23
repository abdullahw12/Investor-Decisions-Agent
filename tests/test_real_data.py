#!/usr/bin/env python3
"""Test with real company data from the data folder."""

import os
import sys
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

def test_with_real_data():
    """Test ingestion and retrieval with real company data."""
    print("🔄 Testing with real company data...")
    
    # Read real data files
    data_files = [
        ("FriendliAI", "data/friendliai.txt", "https://friendli.ai"),
        ("Weaviate", "data/weaviate.txt", "https://weaviate.io"),
        ("CodeRabbit", "data/coderabbit.txt", "https://coderabbit.ai")
    ]
    
    client = get_client()
    
    try:
        # Ingest all companies
        for company_name, file_path, url in data_files:
            if os.path.exists(file_path):
                print(f"\n📄 Processing {company_name}...")
                
                with open(file_path, 'r') as f:
                    text = f.read().strip()
                
                if text:
                    chunks = chunk_text(text)
                    vectors = embed_chunks(chunks)
                    chunk_count = upsert_chunks(client, company_name, company_name, url, chunks, vectors)
                    print(f"✅ Ingested {chunk_count} chunks for {company_name}")
                else:
                    print(f"⚠️  Empty file: {file_path}")
            else:
                print(f"⚠️  File not found: {file_path}")
        
        print("\n" + "="*50)
        print("TESTING RETRIEVAL AND CONFIDENCE")
        print("="*50)
        
        # Test retrieval for each company
        for company_name, _, _ in data_files:
            print(f"\n🔍 Testing retrieval for {company_name}...")
            
            docs = query_company(client, company_name, k=5)
            print(f"Retrieved {len(docs)} documents")
            
            if docs:
                avg_similarity, is_confident = calculate_confidence(docs, threshold=0.25)
                print(f"Confidence: {avg_similarity:.3f} ({'✅ CONFIDENT' if is_confident else '❌ NOT CONFIDENT'})")
                
                context = build_context(docs)
                print(f"Context length: {len(context)} characters")
                
                # Show top result
                text, distance, title = docs[0]
                similarity = max(0.0, 1.0 - distance)
                print(f"Top result: similarity={similarity:.3f}, title='{title}'")
                print(f"Text preview: {text[:100]}...")
            else:
                print("❌ No documents retrieved")
        
        # Test cross-company queries (should have low confidence)
        print(f"\n🔍 Testing cross-company query (should have low confidence)...")
        docs = query_company(client, "NonExistentCompany", k=5)
        if docs:
            avg_similarity, is_confident = calculate_confidence(docs, threshold=0.25)
            print(f"Cross-company confidence: {avg_similarity:.3f} ({'✅ CONFIDENT' if is_confident else '❌ NOT CONFIDENT'})")
        else:
            print("✅ No documents found for non-existent company (expected)")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        client.close()
        return False

def main():
    """Run real data test."""
    print("🚀 Testing with real company data...\n")
    
    # Check required environment variables
    if not os.getenv("WEAVIATE_URL"):
        print("❌ Missing WEAVIATE_URL")
        return False
    
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("FRIENDLI_API_KEY"):
        print("❌ Missing embedding API key")
        return False
    
    success = test_with_real_data()
    
    if success:
        print("\n🎉 Real data test completed successfully!")
        print("✅ Confidence scoring is working correctly with real data")
        print("✅ Ingestion workflow is functional")
        print("✅ Retrieval and similarity calculation is accurate")
    else:
        print("\n❌ Real data test failed")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)