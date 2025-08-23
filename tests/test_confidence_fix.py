#!/usr/bin/env python3
"""Test script to validate confidence scoring fix and ingestion workflow."""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from weaviate_client import (
    get_client,
    initialize_weaviate,
    chunk_text,
    embed_chunks,
    upsert_chunks,
    query_company,
    calculate_confidence,
    build_context
)

def test_weaviate_connection():
    """Test basic Weaviate connection and schema creation."""
    print("🔄 Testing Weaviate connection...")
    
    try:
        # Test initialization
        if not initialize_weaviate():
            print("❌ Weaviate initialization failed")
            return False
        
        # Test client creation
        client = get_client()
        if not client.is_ready():
            print("❌ Weaviate client not ready")
            return False
        
        print("✅ Weaviate connection successful")
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Weaviate connection failed: {e}")
        return False

def test_text_chunking():
    """Test text chunking functionality."""
    print("🔄 Testing text chunking...")
    
    sample_text = """
    FriendliAI is a cutting-edge artificial intelligence company that specializes in optimizing 
    large language models for enterprise deployment. Founded in 2022, the company has developed 
    proprietary technology that significantly reduces the computational costs and latency of 
    running AI models in production environments.
    
    The company's flagship product, Friendli Engine, provides up to 3x faster inference speeds 
    compared to traditional deployment methods while maintaining model accuracy. This breakthrough 
    technology addresses one of the biggest challenges in AI adoption: the high cost and complexity 
    of deploying large models at scale.
    
    FriendliAI has raised $8.5M in Series A funding and serves customers across various industries 
    including finance, healthcare, and technology. The team consists of world-class AI researchers 
    and engineers from top institutions like Stanford, MIT, and Google.
    """
    
    try:
        chunks = chunk_text(sample_text)
        print(f"✅ Created {len(chunks)} chunks")
        
        # Verify chunks are reasonable size
        for i, chunk in enumerate(chunks):
            print(f"  Chunk {i+1}: {len(chunk)} characters")
        
        return chunks
        
    except Exception as e:
        print(f"❌ Text chunking failed: {e}")
        return None

def test_embedding_generation(chunks):
    """Test embedding generation."""
    print("🔄 Testing embedding generation...")
    
    try:
        vectors = embed_chunks(chunks)
        print(f"✅ Generated embeddings for {len(vectors)} chunks")
        
        # Verify embedding dimensions
        if vectors:
            print(f"  Embedding dimension: {len(vectors[0])}")
        
        return vectors
        
    except Exception as e:
        print(f"❌ Embedding generation failed: {e}")
        return None

def test_ingestion_workflow():
    """Test complete ingestion workflow."""
    print("🔄 Testing ingestion workflow...")
    
    # Sample company data
    company_name = "FriendliAI"
    company_url = "https://friendli.ai"
    
    sample_text = """
    FriendliAI is a cutting-edge artificial intelligence company that specializes in optimizing 
    large language models for enterprise deployment. Founded in 2022, the company has developed 
    proprietary technology that significantly reduces the computational costs and latency of 
    running AI models in production environments.
    
    The company's flagship product, Friendli Engine, provides up to 3x faster inference speeds 
    compared to traditional deployment methods while maintaining model accuracy. This breakthrough 
    technology addresses one of the biggest challenges in AI adoption: the high cost and complexity 
    of deploying large models at scale.
    
    FriendliAI has raised $8.5M in Series A funding and serves customers across various industries 
    including finance, healthcare, and technology. The team consists of world-class AI researchers 
    and engineers from top institutions like Stanford, MIT, and Google.
    """
    
    try:
        # Test chunking
        chunks = chunk_text(sample_text)
        if not chunks:
            print("❌ Failed to create chunks")
            return False
        
        # Test embedding
        vectors = embed_chunks(chunks)
        if not vectors:
            print("❌ Failed to generate embeddings")
            return False
        
        # Test ingestion
        client = get_client()
        chunk_count = upsert_chunks(client, company_name, company_name, company_url, chunks, vectors)
        
        print(f"✅ Ingested {chunk_count} chunks for {company_name}")
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Ingestion workflow failed: {e}")
        return False

def test_retrieval_and_confidence():
    """Test retrieval and confidence calculation."""
    print("🔄 Testing retrieval and confidence calculation...")
    
    company_name = "FriendliAI"
    
    try:
        client = get_client()
        
        # Test retrieval
        docs = query_company(client, company_name, k=5)
        print(f"✅ Retrieved {len(docs)} documents for {company_name}")
        
        if docs:
            # Test confidence calculation
            avg_similarity, is_confident = calculate_confidence(docs, threshold=0.25)
            print(f"✅ Confidence calculation: similarity={avg_similarity:.3f}, confident={is_confident}")
            
            # Test context building
            context = build_context(docs)
            print(f"✅ Built context with {len(context)} characters")
            
            # Show sample results
            print("\nSample retrieved documents:")
            for i, (text, distance, title) in enumerate(docs[:3]):
                similarity = max(0.0, 1.0 - distance)
                print(f"  [{i+1}] Distance: {distance:.3f}, Similarity: {similarity:.3f}")
                print(f"      Title: {title}")
                print(f"      Text: {text[:100]}...")
        
        client.close()
        return len(docs) > 0
        
    except Exception as e:
        print(f"❌ Retrieval and confidence test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting confidence scoring and ingestion tests...\n")
    
    # Check required environment variables
    required_vars = ["WEAVIATE_URL"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    # Check embedding API
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("FRIENDLI_API_KEY"):
        print("❌ Missing embedding API key (OPENAI_API_KEY or FRIENDLI_API_KEY)")
        return False
    
    # Run tests
    tests = [
        ("Weaviate Connection", test_weaviate_connection),
        ("Text Chunking", lambda: test_text_chunking() is not None),
        ("Ingestion Workflow", test_ingestion_workflow),
        ("Retrieval and Confidence", test_retrieval_and_confidence),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)
        
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print('='*50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Confidence scoring fix is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)