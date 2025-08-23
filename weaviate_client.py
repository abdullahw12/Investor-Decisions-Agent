"""Utilities for interacting with a Weaviate instance."""
from __future__ import annotations

import os
from typing import Iterable, List, Tuple

import tiktoken
import weaviate
import weaviate.classes as wvc
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

CLASS_NAME = "CompanyDoc"
CHUNK_SIZE = 600  # tokens


def get_client():
    """Create a Weaviate client using environment variables."""
    url = os.getenv("WEAVIATE_URL")
    api_key = os.getenv("WEAVIATE_API_KEY")
    if not url:
        raise ValueError("WEAVIATE_URL is not set")
    
    # Use Weaviate v4 client
    if api_key:
        client = weaviate.connect_to_weaviate_cloud(
            cluster_url=url,
            auth_credentials=wvc.init.Auth.api_key(api_key)
        )
    else:
        client = weaviate.connect_to_custom(
            http_host=url.replace("https://", "").replace("http://", ""),
            http_port=443 if "https" in url else 80,
            http_secure="https" in url
        )
    return client


def initialize_weaviate() -> bool:
    """Initialize Weaviate connection and ensure schema exists at startup."""
    try:
        print("🔄 Initializing Weaviate connection...")
        client = get_client()
        
        # Test connection
        if not client.is_ready():
            print("❌ Weaviate is not ready")
            client.close()
            return False
        
        print("✅ Weaviate connection established")
        
        # Ensure schema exists
        if not ensure_schema(client):
            print("❌ Failed to create Weaviate schema")
            client.close()
            return False
        
        client.close()
        print("✅ Weaviate initialization complete")
        return True
        
    except Exception as e:
        print(f"❌ Weaviate initialization failed: {e}")
        return False


def ensure_schema(client) -> bool:
    """Ensure the CompanyDoc class exists. Returns True if successful."""
    try:
        # Check if collection exists
        if not client.collections.exists(CLASS_NAME):
            print(f"Creating Weaviate collection: {CLASS_NAME}")
            # Create collection with v4 syntax
            client.collections.create(
                name=CLASS_NAME,
                vectorizer_config=wvc.config.Configure.Vectorizer.none(),
                properties=[
                    wvc.config.Property(name="name", data_type=wvc.config.DataType.TEXT),
                    wvc.config.Property(name="title", data_type=wvc.config.DataType.TEXT),
                    wvc.config.Property(name="url", data_type=wvc.config.DataType.TEXT),
                    wvc.config.Property(name="text", data_type=wvc.config.DataType.TEXT),
                ]
            )
            print(f"✅ Created collection: {CLASS_NAME}")
        else:
            print(f"✅ Collection {CLASS_NAME} already exists")
        return True
    except Exception as e:
        print(f"❌ Schema creation error: {e}")
        return False


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE) -> List[str]:
    """Split text into roughly token-sized chunks."""
    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(text)
    chunks = []
    for i in range(0, len(tokens), chunk_size):
        chunk_tokens = tokens[i : i + chunk_size]
        chunks.append(enc.decode(chunk_tokens))
    return chunks


def embed_chunks(chunks: Iterable[str]) -> List[List[float]]:
    """Embed chunks using the OpenAI embedding endpoint."""
    # Try OpenAI first (more reliable for embeddings)
    openai_key = os.getenv("OPENAI_API_KEY")
    friendli_key = os.getenv("FRIENDLI_API_KEY")
    
    if openai_key:
        client = OpenAI(api_key=openai_key)
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=list(chunks),
        )
        return [d.embedding for d in response.data]
    elif friendli_key:
        # Use FriendliAI for embeddings (if they support it)
        client = OpenAI(
            api_key=friendli_key,
            base_url="https://inference.friendli.ai/v1"  # FriendliAI base URL
        )
        try:
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=list(chunks),
            )
            return [d.embedding for d in response.data]
        except Exception:
            # Fallback: FriendliAI might not support embeddings
            raise ValueError("No working embedding API key provided. Please set OPENAI_API_KEY for embeddings.")
    else:
        raise ValueError("No embedding API key provided")


def upsert_chunks(
    client,
    name: str,
    title: str,
    url: str,
    chunks: List[str],
    vectors: List[List[float]],
) -> int:
    """Upsert embedded chunks into Weaviate. Returns number of chunks inserted."""
    # Schema should already be created at startup, but check just in case
    if not ensure_schema(client):
        raise RuntimeError("Failed to ensure Weaviate schema exists")
    
    collection = client.collections.get(CLASS_NAME)
    
    # Delete existing chunks for this company first to avoid duplicates
    try:
        collection.data.delete_many(
            where=wvc.query.Filter.by_property("name").equal(name)
        )
        print(f"Deleted existing chunks for company: {name}")
    except Exception as e:
        print(f"Warning: Could not delete existing chunks: {e}")
    
    # Insert objects with vectors
    objects = []
    for idx, (text, vector) in enumerate(zip(chunks, vectors)):
        objects.append(wvc.data.DataObject(
            properties={
                "name": name,
                "title": title,
                "url": url,
                "text": text,
            },
            vector=vector
        ))
    
    result = collection.data.insert_many(objects)
    print(f"✅ Inserted {len(objects)} chunks for {name}")
    return len(objects)


def query_company(
    client, name: str, k: int = 5
) -> List[Tuple[str, float, str]]:
    """Retrieve top-k chunks for a company by name and semantic similarity."""
    collection = client.collections.get(CLASS_NAME)
    
    try:
        # Method 1: Try vector search without where filter, then filter manually
        query_vector = embed_chunks([name])[0]
        
        response = collection.query.near_vector(
            near_vector=query_vector,
            limit=k * 3,  # Get more results to filter
            return_metadata=wvc.query.MetadataQuery(distance=True)
        )
        
        # Filter results manually by company name
        docs = []
        for obj in response.objects:
            obj_name = obj.properties.get("name", "")
            if obj_name.lower() == name.lower():
                text = obj.properties.get("text", "")
                title = obj.properties.get("title", "")
                distance = obj.metadata.distance if obj.metadata else 1.0
                docs.append((text, distance, title))
                
                if len(docs) >= k:  # Stop when we have enough results
                    break
        
        return docs
        
    except Exception as e:
        print(f"Vector search failed: {e}")
        
        # Fallback: Use bm25 search if available
        try:
            response = collection.query.bm25(
                query=name,
                limit=k * 2,
                return_metadata=wvc.query.MetadataQuery(score=True)
            )
            
            # Filter results manually by company name
            docs = []
            for obj in response.objects:
                obj_name = obj.properties.get("name", "")
                if obj_name.lower() == name.lower():
                    text = obj.properties.get("text", "")
                    title = obj.properties.get("title", "")
                    # Convert BM25 score to distance-like metric
                    score = obj.metadata.score if obj.metadata else 0.0
                    distance = max(0.0, 1.0 - score)  # Convert score to distance
                    docs.append((text, distance, title))
                    
                    if len(docs) >= k:
                        break
            
            return docs
            
        except Exception as e2:
            print(f"BM25 search also failed: {e2}")
            
            # Final fallback: Get all objects and filter
            try:
                response = collection.query.fetch_objects(
                    limit=100,  # Get a reasonable number of objects
                    return_metadata=wvc.query.MetadataQuery()
                )
                
                docs = []
                for obj in response.objects:
                    obj_name = obj.properties.get("name", "")
                    if obj_name.lower() == name.lower():
                        text = obj.properties.get("text", "")
                        title = obj.properties.get("title", "")
                        # Use default distance since we can't calculate similarity
                        distance = 0.3  # Assume reasonable similarity
                        docs.append((text, distance, title))
                        
                        if len(docs) >= k:
                            break
                
                return docs
                
            except Exception as e3:
                print(f"Final fallback also failed: {e3}")
                return []


def calculate_confidence(docs: List[Tuple[str, float, str]], threshold: float = 0.25) -> Tuple[float, bool]:
    """
    Calculate confidence score from retrieved documents.
    
    Args:
        docs: List of (text, distance, title) tuples from Weaviate
        threshold: Minimum similarity threshold (default 0.25)
    
    Returns:
        Tuple of (average_similarity, is_confident)
    """
    if not docs:
        return 0.0, False
    
    # Convert distances to similarities (distance = 1 - similarity in cosine space)
    similarities = [max(0.0, 1.0 - distance) for _, distance, _ in docs]
    
    # Calculate average similarity of top 3 results
    top_similarities = similarities[:min(3, len(similarities))]
    avg_similarity = sum(top_similarities) / len(top_similarities)
    
    # Check if confidence is above threshold
    is_confident = avg_similarity >= threshold
    
    print(f"Confidence calculation: avg_similarity={avg_similarity:.3f}, threshold={threshold}, confident={is_confident}")
    return avg_similarity, is_confident


def build_context(docs: List[Tuple[str, float, str]]) -> str:
    """Build context string with numbered citations."""
    lines = []
    for i, (text, _dist, title) in enumerate(docs, start=1):
        snippet = text.replace("\n", " ")[:200]
        lines.append(f"[{i}] {title} :: {snippet}")
    return "\n".join(lines)
