#!/usr/bin/env python3
"""
Create MVP dataset with ~50 curated shlokas from all topics.
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / 'data'

def create_mvp_dataset():
    """Extract curated shlokas for MVP."""

    # Load all shlokas
    with open(DATA_DIR / 'gita_tagged.json', 'r', encoding='utf-8') as f:
        all_shlokas = json.load(f)

    # Load curated topics
    with open(DATA_DIR / 'curated_topics.json', 'r', encoding='utf-8') as f:
        curated_topics = json.load(f)

    # Collect unique shloka IDs from all curated topics
    mvp_ids = set()
    for topic_id, topic_info in curated_topics.items():
        for shloka_id in topic_info.get('best_shlokas', []):
            mvp_ids.add(shloka_id)

    # Add some famous universal shlokas
    universal_ids = ['2.47', '18.66', '4.7', '4.8', '9.22', '11.32', '15.15']
    for sid in universal_ids:
        mvp_ids.add(sid)

    print(f"Total unique shloka IDs: {len(mvp_ids)}")

    # Create lookup
    shloka_lookup = {s['shloka_id']: s for s in all_shlokas}

    # Extract MVP shlokas
    mvp_shlokas = []
    for shloka_id in sorted(mvp_ids, key=lambda x: (int(x.split('.')[0]), int(x.split('.')[1]))):
        if shloka_id in shloka_lookup:
            mvp_shlokas.append(shloka_lookup[shloka_id])
        else:
            print(f"Warning: {shloka_id} not found")

    print(f"MVP shlokas extracted: {len(mvp_shlokas)}")

    # Save MVP dataset
    output_path = DATA_DIR / 'gita_mvp.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(mvp_shlokas, f, ensure_ascii=False, indent=2)

    print(f"Saved to: {output_path}")

    # Print shloka IDs for reference
    print("\nMVP Shloka IDs:")
    print([s['shloka_id'] for s in mvp_shlokas])

if __name__ == '__main__':
    create_mvp_dataset()
