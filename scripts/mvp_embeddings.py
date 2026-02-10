#!/usr/bin/env python3
"""
Generate enriched embeddings for all shlokas using Cohere and store in ChromaDB.
Embeds: topic keywords (Hindi + English) + hindi meaning for better semantic matching.
"""

import json
import os
from pathlib import Path

import cohere
import chromadb

DATA_DIR = Path(__file__).parent.parent / 'data'
CHROMADB_DIR = DATA_DIR / 'chromadb_full'

# Short Hindi label per topic — one keyword each, used as tags
TOPIC_HINDI = {
    'dharma': 'धर्म', 'karma': 'कर्म', 'bhakti': 'भक्ति', 'gyan': 'ज्ञान',
    'atma': 'आत्मा', 'mrityu': 'मृत्यु', 'krodh': 'क्रोध', 'bhay': 'भय',
    'shanti': 'शांति', 'dukh': 'दुख', 'sukh': 'सुख', 'moha': 'मोह',
    'tyag': 'त्याग', 'man': 'मन', 'parivar': 'परिवार', 'shraddha': 'श्रद्धा',
    'dhyan': 'ध्यान', 'samatva': 'समत्व', 'indriya': 'इन्द्रिय',
    'nishkam_karma': 'निष्काम कर्म', 'sharanagati': 'शरणागति', 'prem': 'प्रेम',
    'sahas': 'साहस', 'ahankar': 'अहंकार', 'sansar': 'संसार',
    'swadharma': 'स्वधर्म', 'guru': 'गुरु', 'sewa': 'सेवा',
    'nishtha': 'निष्ठा', 'paap': 'पाप', 'punya': 'पुण्य',
    'satvik': 'सात्विक', 'rajasik': 'राजसिक', 'tamasik': 'तामसिक',
    'yuddh': 'संघर्ष', 'kaal': 'काल', 'avatar': 'अवतार',
}

# Rare/specific topics are more discriminative than common ones
# Topics appearing in 200+ shlokas are too generic to be useful
COMMON_TOPICS = {'karma', 'dharma', 'yuddh', 'parivar', 'sansar'}


def prepare_embedding_text(shloka: dict, topics: list[str]) -> str:
    """Prepare enriched text: meaning first, then specific topic tags."""
    meaning = shloka.get('hindi_meaning', '')[:600]
    # Only use specific/rare topics as tags (skip overly common ones)
    specific_topics = [t for t in topics if t not in COMMON_TOPICS][:5]
    tags = ', '.join(TOPIC_HINDI.get(t, t) for t in specific_topics)
    if tags:
        return f"{meaning}\nविषय: {tags}"
    return meaning


def generate_embeddings():
    """Generate enriched embeddings and store in ChromaDB."""

    api_key = os.environ.get('COHERE_API_KEY')
    if not api_key:
        print("Error: COHERE_API_KEY environment variable not set")
        return

    # Load all 701 shlokas (complete Gita)
    with open(DATA_DIR / 'raw' / 'gita_complete.json', 'r', encoding='utf-8') as f:
        shlokas = json.load(f)

    # Load topic index and build reverse mapping (shloka -> topics)
    with open(DATA_DIR / 'topic_index.json', 'r', encoding='utf-8') as f:
        topic_index = json.load(f)

    shloka_topics = {}
    for topic, sids in topic_index.items():
        for sid in sids:
            shloka_topics.setdefault(sid, []).append(topic)

    print(f"Loaded {len(shlokas)} shlokas, {len(shloka_topics)} with topic assignments")

    co = cohere.Client(api_key)

    texts = []
    ids = []
    metadatas = []

    for shloka in shlokas:
        sid = shloka['shloka_id']
        topics = shloka_topics.get(sid, [])
        text = prepare_embedding_text(shloka, topics)
        texts.append(text)
        ids.append(sid)
        metadatas.append({
            'chapter': shloka['chapter'],
            'verse': shloka['verse'],
            'shloka_id': sid,
        })

    print(f"Generating embeddings for {len(texts)} texts...")
    print(f"Example embedding text for 2.47:\n{texts[ids.index('2.47')][:300]}...\n")

    all_embeddings = []
    batch_size = 96

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        batch_num = i // batch_size + 1
        total_batches = (len(texts) + batch_size - 1) // batch_size
        print(f"  Batch {batch_num}/{total_batches}...")

        response = co.embed(
            texts=batch,
            model="embed-multilingual-v3.0",
            input_type="search_document",
            truncate="END"
        )
        all_embeddings.extend(response.embeddings)

    print(f"Generated {len(all_embeddings)} embeddings")

    CHROMADB_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMADB_DIR))

    try:
        client.delete_collection("gita_full")
        print("Deleted existing collection")
    except Exception:
        pass

    collection = client.create_collection(
        name="gita_full",
        metadata={"hnsw:space": "cosine"}
    )

    collection.add(
        ids=ids,
        embeddings=all_embeddings,
        metadatas=metadatas,
        documents=texts
    )

    print(f"Stored {len(ids)} embeddings in ChromaDB at {CHROMADB_DIR}")
    print("Done!")


if __name__ == '__main__':
    generate_embeddings()
