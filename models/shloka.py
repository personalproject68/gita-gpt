"""Shloka data model and lookup."""

import json
import random
from datetime import date
from config import DATA_DIR

def load_shlokas():
    with open(DATA_DIR / 'gita_mvp.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_complete_shlokas():
    """Load all 701 shlokas for the Gita Journey."""
    with open(DATA_DIR / 'raw' / 'gita_complete.json', 'r', encoding='utf-8') as f:
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

# Complete 701 shlokas for Gita Journey (sequential)
COMPLETE_SHLOKAS = _clean_shlokas(load_complete_shlokas())
COMPLETE_LOOKUP = {s['shloka_id']: s for s in COMPLETE_SHLOKAS}

# Chapter names in Hindi
CHAPTER_NAMES = {
    1: "अर्जुनविषादयोग", 2: "सांख्ययोग", 3: "कर्मयोग",
    4: "ज्ञानकर्मसन्यासयोग", 5: "कर्मसन्यासयोग", 6: "आत्मसंयमयोग",
    7: "ज्ञानविज्ञानयोग", 8: "अक्षरब्रह्मयोग", 9: "राजविद्याराजगुह्ययोग",
    10: "विभूतियोग", 11: "विश्वरूपदर्शनयोग", 12: "भक्तियोग",
    13: "क्षेत्रक्षेत्रज्ञविभागयोग", 14: "गुणत्रयविभागयोग", 15: "पुरुषोत्तमयोग",
    16: "दैवासुरसम्पद्विभागयोग", 17: "श्रद्धात्रयविभागयोग", 18: "मोक्षसन्यासयोग",
}

# Pre-compute chapter boundaries (position ranges)
_CHAPTER_BOUNDS = {}
for _i, _s in enumerate(COMPLETE_SHLOKAS):
    _ch = _s['chapter']
    if _ch not in _CHAPTER_BOUNDS:
        _CHAPTER_BOUNDS[_ch] = {'first': _i, 'last': _i}
    else:
        _CHAPTER_BOUNDS[_ch]['last'] = _i


def get_shloka_by_id(shloka_id: str) -> dict | None:
    return SHLOKA_LOOKUP.get(shloka_id)


def get_journey_shloka(position: int) -> dict | None:
    """Get shloka at a given journey position (0-indexed)."""
    if 0 <= position < len(COMPLETE_SHLOKAS):
        return COMPLETE_SHLOKAS[position]
    return None


def get_chapter_info(position: int) -> dict | None:
    """Get chapter info for a given journey position."""
    if position < 0 or position >= len(COMPLETE_SHLOKAS):
        return None
    shloka = COMPLETE_SHLOKAS[position]
    ch = shloka['chapter']
    bounds = _CHAPTER_BOUNDS[ch]
    return {
        'chapter': ch,
        'name_hi': CHAPTER_NAMES.get(ch, ''),
        'first_position': bounds['first'],
        'last_position': bounds['last'],
    }


def is_chapter_complete(position: int) -> bool:
    """Check if this position is the last shloka of its chapter."""
    info = get_chapter_info(position)
    return info is not None and position == info['last_position']


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
