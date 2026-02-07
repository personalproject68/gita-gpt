#!/usr/bin/env python3
"""Fetch Hindi interpretations for all 99 curated shlokas from vedicscriptures GitHub."""

import json
import sys
import time
import requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

DATA_DIR = Path(__file__).parent.parent / 'data'
BASE_URL = "https://raw.githubusercontent.com/vedicscriptures/bhagavad-gita/main/slok"


def fetch_shloka(chapter: int, verse: int) -> dict | None:
    url = f"{BASE_URL}/bhagavadgita_chapter_{chapter}_slok_{verse}.json"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print(f"  Error: {e}")
    return None


def extract_hindi_interpretation(data: dict) -> str:
    """Extract the best Hindi interpretation from available commentaries."""
    # Priority order: Ramsukhdas (simplest Hindi), Tejomayananda, Shankaracharya
    for key in ['rams', 'tej', 'sankar', 'chinmay', 'san', 'adi']:
        if key in data and isinstance(data[key], dict):
            ht = data[key].get('ht', '')
            if ht and len(ht) > 20:
                # Clean up - remove verse reference prefix like "।।2.47।।"
                lines = ht.strip().split('\n')
                clean = '\n'.join(lines).strip()
                # Truncate to reasonable length
                if len(clean) > 500:
                    clean = clean[:497] + '...'
                return clean
    return ""


def main():
    # Load curated shlokas
    with open(DATA_DIR / 'gita_mvp.json', 'r', encoding='utf-8') as f:
        shlokas = json.load(f)

    print(f"Fetching interpretations for {len(shlokas)} shlokas...")

    interpretations = {}
    success, failed = 0, 0

    for i, shloka in enumerate(shlokas):
        sid = shloka['shloka_id']
        parts = sid.split('.')
        chapter, verse = int(parts[0]), int(parts[1])

        print(f"  [{i+1}/{len(shlokas)}] {sid}...", end=' ', flush=True)

        data = fetch_shloka(chapter, verse)
        if data:
            interp = extract_hindi_interpretation(data)
            if interp:
                interpretations[sid] = interp
                success += 1
                print(f"OK ({len(interp)} chars)")
            else:
                failed += 1
                print("no Hindi text")
        else:
            failed += 1
            print("FAILED")

        # Be nice to GitHub
        time.sleep(0.3)

    # Save
    out_path = DATA_DIR / 'interpretations.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(interpretations, f, ensure_ascii=False, indent=2)

    print(f"\nDone! {success} interpretations saved, {failed} failed")
    print(f"Saved to: {out_path}")


if __name__ == '__main__':
    main()
