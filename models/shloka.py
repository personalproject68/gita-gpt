"""Shloka data model and lookup."""

import json
import random
from config import DATA_DIR

def load_shlokas():
    with open(DATA_DIR / 'gita_mvp.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_curated_topics():
    with open(DATA_DIR / 'curated_topics.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_topic_index():
    path = DATA_DIR / 'topic_index.json'
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def _clean_shlokas(shlokas):
    """Safety net: replace placeholders and handle grouped verses."""
    for i, s in enumerate(shlokas):
        m = s.get('hindi_meaning', '')
        c = s.get('hindi_commentary', '')
        
        # Detect any placeholder text
        is_placeholder = (
            'did not comment' in m.lower() or 
            'no commentary' in m.lower() or
            len(m.strip()) < 5
        )
        
        if is_placeholder:
            # Look forward for the group's meaning
            for offset in [1, 2, 3, -1, -2]:
                idx = i + offset
                if 0 <= idx < len(shlokas):
                    partner = shlokas[idx]
                    pm = partner.get('hindi_meaning', '')
                    if pm and 'comment' not in pm.lower() and len(pm) > 10:
                        s['hindi_meaning'] = pm
                        s['hindi_commentary'] = partner.get('hindi_commentary', '')
                        break
    return shlokas

SHLOKAS = _clean_shlokas(load_shlokas())
CURATED_TOPICS = load_curated_topics()
TOPIC_INDEX = load_topic_index()
SHLOKA_LOOKUP = {s['shloka_id']: s for s in SHLOKAS}


def get_shloka_by_id(shloka_id: str) -> dict | None:
    return SHLOKA_LOOKUP.get(shloka_id)


def get_daily_shloka(topic: str = None) -> dict:
    if topic and topic in CURATED_TOPICS:
        shloka_ids = CURATED_TOPICS[topic]['best_shlokas']
        valid = [sid for sid in shloka_ids if sid in SHLOKA_LOOKUP]
        if valid:
            return SHLOKA_LOOKUP[random.choice(valid)]

    famous_ids = ['2.47', '2.14', '2.22', '2.27', '3.35', '4.7', '6.5', '9.22', '18.66']
    valid = [sid for sid in famous_ids if sid in SHLOKA_LOOKUP]
    return SHLOKA_LOOKUP[random.choice(valid)]
