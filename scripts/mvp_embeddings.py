#!/usr/bin/env python3
"""
Generate embeddings for MVP shlokas using Cohere and store in ChromaDB.
"""

import json
import os
from pathlib import Path

import cohere
import chromadb
from chromadb.config import Settings

DATA_DIR = Path(__file__).parent.parent / 'data'
CHROMADB_DIR = DATA_DIR / 'chromadb_mvp'


def prepare_embedding_text(shloka: dict) -> str:
    """
    Prepare text for embedding.
    Combines hindi_meaning and tags for semantic richness.
    """
    meaning = shloka.get('hindi_meaning', '')[:800]  # Truncate for embedding
    tags = ' '.join(shloka.get('tags', []))

    # Combine meaning with tags for better semantic matching
    return f"{meaning} | विषय: {tags}"


def generate_embeddings():
    """Generate embeddings and store in ChromaDB."""

    # Check for API key
    api_key = os.environ.get('COHERE_API_KEY')
    if not api_key:
        print("Error: COHERE_API_KEY environment variable not set")
        print("Get a free API key at: https://dashboard.cohere.com/api-keys")
        return

    # Load MVP shlokas
    with open(DATA_DIR / 'gita_mvp.json', 'r', encoding='utf-8') as f:
        shlokas = json.load(f)

    print(f"Loaded {len(shlokas)} shlokas")

    # Initialize Cohere client
    co = cohere.Client(api_key)

    # Prepare texts for embedding
    texts = []
    ids = []
    metadatas = []

    for shloka in shlokas:
        text = prepare_embedding_text(shloka)
        texts.append(text)
        ids.append(shloka['shloka_id'])
        metadatas.append({
            'chapter': shloka['chapter'],
            'verse': shloka['verse'],
            'shloka_id': shloka['shloka_id'],
            'tags': ','.join(shloka.get('tags', [])),
        })

    print(f"Generating embeddings for {len(texts)} texts...")

    # Generate embeddings (Cohere allows up to 96 per batch)
    all_embeddings = []
    batch_size = 96

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        print(f"  Processing batch {i // batch_size + 1}...")

        response = co.embed(
            texts=batch,
            model="embed-multilingual-v3.0",
            input_type="search_document",
            truncate="END"
        )
        all_embeddings.extend(response.embeddings)

    print(f"Generated {len(all_embeddings)} embeddings")

    # Initialize ChromaDB
    CHROMADB_DIR.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(path=str(CHROMADB_DIR))

    # Delete existing collection if exists
    try:
        client.delete_collection("gita_mvp")
        print("Deleted existing collection")
    except Exception:
        pass

    # Create collection
    collection = client.create_collection(
        name="gita_mvp",
        metadata={"hnsw:space": "cosine"}
    )

    # Add embeddings to collection
    collection.add(
        ids=ids,
        embeddings=all_embeddings,
        metadatas=metadatas,
        documents=texts
    )

    print(f"Stored {len(ids)} embeddings in ChromaDB at {CHROMADB_DIR}")
    print("\nDone! You can now use semantic search in app.py")


if __name__ == '__main__':
    generate_embeddings()
