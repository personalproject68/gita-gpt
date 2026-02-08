"""Shloka data model and lookup."""

import json
import random
from datetime import date
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

    famous_ids = [
        # Chapter 2 — Sankhya Yoga (foundational wisdom)
        '2.7', '2.11', '2.13', '2.14', '2.20', '2.22', '2.27', '2.47', '2.62', '2.70',
        # Chapter 3 — Karma Yoga
        '3.21', '3.27', '3.35',
        # Chapter 4 — Jnana Yoga
        '4.7', '4.8', '4.34', '4.38',
        # Chapter 6 — Dhyana Yoga
        '6.5', '6.6', '6.34',
        # Chapter 9 — Raja Vidya
        '9.22', '9.26', '9.27',
        # Chapter 11-15
        '11.32', '12.13', '15.7',
        # Chapter 18 — Moksha Sannyasa
        '18.20', '18.46', '18.63', '18.66',
    ]
    valid = [sid for sid in famous_ids if sid in SHLOKA_LOOKUP]
    # Cycle through shlokas by date — same shloka for everyone on a given day
    index = date.today().toordinal() % len(valid)
    return SHLOKA_LOOKUP[valid[index]]
