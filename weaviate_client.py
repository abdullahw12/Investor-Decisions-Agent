"""Utilities for interacting with a Weaviate instance."""
from __future__ import annotations

import os
from typing import Iterable, List, Tuple

import tiktoken
import weaviate
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

CLASS_NAME = "CompanyDoc"
CHUNK_SIZE = 600  # tokens


def get_client() -> weaviate.Client:
    """Create a Weaviate client using environment variables."""
    url = os.getenv("WEAVIATE_URL")
    api_key = os.getenv("WEAVIATE_API_KEY")
    if not url:
        raise ValueError("WEAVIATE_URL is not set")
    auth = weaviate.AuthApiKey(api_key) if api_key else None
    client = weaviate.Client(url, auth_client_secret=auth)
    return client


def ensure_schema(client: weaviate.Client) -> None:
    """Ensure the CompanyDoc class exists."""
    schema = {
        "class": CLASS_NAME,
        "vectorizer": "none",
        "properties": [
            {"name": "name", "dataType": ["text"]},
            {"name": "title", "dataType": ["text"]},
            {"name": "url", "dataType": ["text"]},
            {"name": "text", "dataType": ["text"]},
        ],
    }
    if not client.schema.exists(CLASS_NAME):
        client.schema.create_class(schema)


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
    api_key = os.getenv("FRIENDLI_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("No embedding API key provided")
    client = OpenAI(api_key=api_key)
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=list(chunks),
    )
    return [d.embedding for d in response.data]


def upsert_chunks(
    client: weaviate.Client,
    name: str,
    title: str,
    url: str,
    chunks: List[str],
    vectors: List[List[float]],
) -> None:
    """Upsert embedded chunks into Weaviate."""
    ensure_schema(client)
    with client.batch as batch:
        for idx, (text, vector) in enumerate(zip(chunks, vectors)):
            obj = {
                "name": name,
                "title": title,
                "url": url,
                "text": text,
            }
            batch.add_data_object(obj, class_name=CLASS_NAME, vector=vector)


def query_company(
    client: weaviate.Client, name: str, k: int = 5
) -> List[Tuple[str, float, str]]:
    """Retrieve top-k chunks for a company by name and semantic similarity."""
    near_text = {"concepts": [name]}
    result = (
        client.query.get(CLASS_NAME, ["text", "title", "url"])
        .with_where({"path": ["name"], "operator": "Equal", "valueText": name})
        .with_near_text(near_text)
        .with_limit(k)
        .with_additional(["distance"])
        .do()
    )
    docs = result["data"]["Get"].get(CLASS_NAME, [])
    return [(d["text"], d["_additional"]["distance"], d.get("title", "")) for d in docs]


def build_context(docs: List[Tuple[str, float, str]]) -> str:
    """Build context string with numbered citations."""
    lines = []
    for i, (text, _dist, title) in enumerate(docs, start=1):
        snippet = text.replace("\n", " ")[:200]
        lines.append(f"[{i}] {title} :: {snippet}")
    return "\n".join(lines)
