#!/usr/bin/env python3
"""
Generate embeddings for ALL 700 shlokas using Cohere and store in ChromaDB.
"""

import json
import os
from pathlib import Path

import cohere
import chromadb
from dotenv import load_dotenv

# Load env variables for API key
load_dotenv()

DATA_DIR = Path(__file__).parent.parent / 'data'
RAW_DATA_PATH = DATA_DIR / 'raw' / 'gita_complete.json'
CHROMADB_DIR = DATA_DIR / 'chromadb_full'

def prepare_embedding_text(shloka: dict) -> str:
    """
    Prepare text for embedding.
    Combines hindi_meaning and any available tags.
    """
    meaning = shloka.get('hindi_meaning', '')[:1000]
    tags = ' '.join(shloka.get('tags', []))
    
    # Chapter and Verse info context
    context = f"अध्याय {shloka['chapter']}, श्लोक {shloka['verse']}"
    
    return f"{context} | {meaning} | {tags}"

def generate_embeddings():
    """Generate embeddings and store in ChromaDB."""

    api_key = os.environ.get('COHERE_API_KEY')
    if not api_key:
        print("Error: COHERE_API_KEY environment variable not set")
        return

    if not RAW_DATA_PATH.exists():
        print(f"Error: Data file not found at {RAW_DATA_PATH}")
        return

    # Load ALL shlokas
    with open(RAW_DATA_PATH, 'r', encoding='utf-8') as f:
        shlokas = json.load(f)

    print(f"Loaded {len(shlokas)} shlokas from {RAW_DATA_PATH}")

    co = cohere.Client(api_key)

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
            'shloka_id': shloka['shloka_id']
        })

    print(f"Generating embeddings for {len(texts)} shlokas...")

    all_embeddings = []
    batch_size = 96 # Cohere recommended batch size

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        print(f"  Processing batch {i // batch_size + 1}...")

        try:
            response = co.embed(
                texts=batch,
                model="embed-multilingual-v3.0",
                input_type="search_document",
                truncate="END"
            )
            all_embeddings.extend(response.embeddings)
        except Exception as e:
            print(f"Error in batch {i}: {e}")
            return

    print(f"Generated {len(all_embeddings)} embeddings")

    # Initialize ChromaDB
    CHROMADB_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMADB_DIR))

    # Create/Get collection
    try:
        client.delete_collection("gita_full")
    except Exception:
        pass
        
    collection = client.create_collection(
        name="gita_full",
        metadata={"hnsw:space": "cosine"}
    )

    # Add embeddings
    collection.add(
        ids=ids,
        embeddings=all_embeddings,
        metadatas=metadatas,
        documents=texts
    )

    print(f"Stored {len(ids)} embeddings in ChromaDB at {CHROMADB_DIR}")

if __name__ == '__main__':
    generate_embeddings()
