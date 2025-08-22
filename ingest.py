"""Offline ingestion script for one-pager documents."""
from __future__ import annotations

import argparse
from typing import Tuple

from weaviate_client import (
    build_context,
    chunk_text,
    embed_chunks,
    get_client,
    upsert_chunks,
)



def parse_document(path: str) -> Tuple[str, str, str]:
    """Parse a one-pager file into (title, url, body)."""
    with open(path, "r", encoding="utf-8") as f:
        lines = f.read().strip().splitlines()
    header = lines[0]
    title, url = [p.strip() for p in header.split("|", 1)]
    body = "\n".join(lines[1:])
    return title, url, body


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest a startup one-pager")
    parser.add_argument("path", help="Path to one-pager text file")
    parser.add_argument("--name", required=True, help="Canonical company name")
    args = parser.parse_args()

    title, url, body = parse_document(args.path)
    chunks = chunk_text(body)
    vectors = embed_chunks(chunks)

    client = get_client()
    upsert_chunks(client, args.name, title, url, chunks, vectors)
    print(f"Ingested {len(chunks)} chunks for {args.name}")


if __name__ == "__main__":
    main()
