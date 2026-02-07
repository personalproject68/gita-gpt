#!/usr/bin/env python3
"""
Bhagavad Gita Data Fetcher
Fetches all 700 shlokas from the vedicscriptures API and structures them for Gita GPT.
"""

import json
import csv
import time
import urllib.request
import urllib.error
from pathlib import Path

# Verse counts for each chapter (1-18)
CHAPTER_VERSES = {
    1: 47, 2: 72, 3: 43, 4: 42, 5: 29, 6: 47,
    7: 30, 8: 28, 9: 34, 10: 42, 11: 55, 12: 20,
    13: 35, 14: 27, 15: 20, 16: 24, 17: 28, 18: 78
}

API_BASE = "https://vedicscriptures.github.io/slok"

def fetch_shloka(chapter: int, verse: int) -> dict | None:
    """Fetch a single shloka from the API."""
    url = f"{API_BASE}/{chapter}/{verse}"
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.URLError as e:
        print(f"  Error fetching {chapter}.{verse}: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"  JSON error for {chapter}.{verse}: {e}")
        return None

def extract_hindi_translation(data: dict) -> tuple[str, str, str]:
    """
    Extract Hindi translation from available commentators.
    Priority: Ramsukhdas > Tejomayananda > Chinmayananda > others
    Returns: (hindi_translation, hindi_commentary, author)
    """
    # Priority order - Ramsukhdas is known for simple Hindi
    priority = ['rams', 'tej', 'chinmay', 'sankar', 'jaya', 'vallabh', 'ms', 'srid', 'dhan', 'venkat', 'puru', 'neel']

    for key in priority:
        if key in data and data[key]:
            commentator = data[key]
            ht = commentator.get('ht', '')  # Hindi translation
            hc = commentator.get('hc', '')  # Hindi commentary
            author = commentator.get('author', key)
            if ht:  # Only return if Hindi translation exists
                return (ht, hc, author)

    # Fallback: check all keys for any Hindi translation
    for key, value in data.items():
        if isinstance(value, dict) and value.get('ht'):
            return (value['ht'], value.get('hc', ''), value.get('author', key))

    return ('', '', '')

def process_shloka(data: dict) -> dict:
    """Process raw API data into clean structure."""
    hindi_translation, hindi_commentary, author = extract_hindi_translation(data)

    return {
        'chapter': data.get('chapter', 0),
        'verse': data.get('verse', 0),
        'shloka_id': f"{data.get('chapter', 0)}.{data.get('verse', 0)}",
        'sanskrit': data.get('slok', ''),
        'transliteration': data.get('transliteration', ''),
        'hindi_meaning': hindi_translation,
        'hindi_commentary': hindi_commentary,
        'translation_author': author,
        'tags': [],  # To be filled manually
        'situations': []  # To be filled manually - when to use this shloka
    }

def fetch_all_shlokas() -> list[dict]:
    """Fetch all 700 shlokas from the API."""
    all_shlokas = []
    total = sum(CHAPTER_VERSES.values())
    count = 0

    for chapter, num_verses in CHAPTER_VERSES.items():
        print(f"\nChapter {chapter} ({num_verses} verses):")

        for verse in range(1, num_verses + 1):
            count += 1
            print(f"  Fetching {chapter}.{verse} ({count}/{total})...", end=' ')

            raw_data = fetch_shloka(chapter, verse)
            if raw_data:
                processed = process_shloka(raw_data)
                all_shlokas.append(processed)
                print("OK")
            else:
                print("FAILED")

            # Be nice to the API
            time.sleep(0.1)

    return all_shlokas

def save_json(data: list[dict], filepath: Path):
    """Save data as JSON."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved JSON: {filepath}")

def save_csv(data: list[dict], filepath: Path):
    """Save data as CSV."""
    if not data:
        return

    # Flatten tags and situations for CSV
    csv_data = []
    for item in data:
        row = item.copy()
        row['tags'] = '|'.join(row['tags']) if row['tags'] else ''
        row['situations'] = '|'.join(row['situations']) if row['situations'] else ''
        csv_data.append(row)

    fieldnames = ['shloka_id', 'chapter', 'verse', 'sanskrit', 'transliteration',
                  'hindi_meaning', 'hindi_commentary', 'translation_author', 'tags', 'situations']

    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_data)
    print(f"Saved CSV: {filepath}")

def main():
    """Main function to fetch and save all Gita data."""
    print("=" * 60)
    print("Bhagavad Gita Data Fetcher for Gita GPT")
    print("=" * 60)
    print(f"Total chapters: 18")
    print(f"Total shlokas: {sum(CHAPTER_VERSES.values())}")
    print("=" * 60)

    # Fetch all shlokas
    shlokas = fetch_all_shlokas()

    print(f"\n{'=' * 60}")
    print(f"Fetched {len(shlokas)} shlokas successfully")
    print("=" * 60)

    # Save to files
    data_dir = Path(__file__).parent.parent / 'data'
    data_dir.mkdir(exist_ok=True)

    save_json(shlokas, data_dir / 'gita_complete.json')
    save_csv(shlokas, data_dir / 'gita_complete.csv')

    # Also save a simplified version for quick reference
    simple_data = [
        {
            'id': s['shloka_id'],
            'sanskrit': s['sanskrit'],
            'hindi': s['hindi_meaning'],
            'tags': s['tags']
        }
        for s in shlokas
    ]
    save_json(simple_data, data_dir / 'gita_simple.json')

    print("\nDone! Files saved in data/ directory")
    print("\nNext steps:")
    print("1. Review gita_complete.csv")
    print("2. Add tags to each shloka based on themes")
    print("3. Add 'situations' - when to use each shloka")

if __name__ == '__main__':
    main()
