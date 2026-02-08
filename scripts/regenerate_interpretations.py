#!/usr/bin/env python3
"""Batch-regenerate interpretations.json with [SECTION] format (shabdarth + bhavarth).

Usage: python scripts/regenerate_interpretations.py
"""

import json
import sys
import time
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from config import DATA_DIR, GOOGLE_API_KEY

PROMPT = """आप श्रीमद्भगवद्गीता के विद्वान हैं। केवल नीचे दिए गए एक श्लोक के लिए output दें। किसी अन्य श्लोक का उल्लेख न करें।

श्लोक:
{sanskrit}

अर्थ: {hindi_meaning}

कृपया ठीक दो भाग लिखें, हर भाग को "[SECTION]" से अलग करें:

भाग 1 — शब्दार्थ (1 पंक्ति): केवल इस श्लोक के मुख्य संस्कृत शब्दों का हिंदी अर्थ, pipe (|) से अलग।
उदाहरण: यदा यदा = जब-जब | धर्मस्य = धर्म की | ग्लानिः = हानि

भाग 2 — भावार्थ (2-3 वाक्य): श्लोक का सरल हिंदी अर्थ। शुद्ध सरल हिंदी।

बिल्कुल न लिखें: कोई heading, label, श्लोक संख्या, "शब्दार्थ:", "भावार्थ:" जैसे prefix, या कोई अन्य श्लोक।
सिर्फ content लिखें, [SECTION] से अलग करें। संक्षिप्त रखें।"""


def get_key_shloka_ids():
    """Get union of daily famous_ids + curated topic shloka IDs."""
    famous_ids = [
        '2.7', '2.11', '2.13', '2.14', '2.20', '2.22', '2.27', '2.47', '2.62', '2.70',
        '3.21', '3.27', '3.35',
        '4.7', '4.8', '4.34', '4.38',
        '6.5', '6.6', '6.34',
        '9.22', '9.26', '9.27',
        '11.32', '12.13', '15.7',
        '18.20', '18.46', '18.63', '18.66',
    ]

    curated_path = DATA_DIR / 'curated_topics.json'
    curated_ids = []
    if curated_path.exists():
        with open(curated_path, 'r', encoding='utf-8') as f:
            topics = json.load(f)
        for topic_data in topics.values():
            curated_ids.extend(topic_data.get('best_shlokas', []))

    all_ids = sorted(set(famous_ids + curated_ids), key=lambda x: (int(x.split('.')[0]), int(x.split('.')[1])))
    return all_ids


def main():
    if not GOOGLE_API_KEY:
        print("ERROR: GOOGLE_API_KEY not set")
        sys.exit(1)

    from google import genai
    client = genai.Client(api_key=GOOGLE_API_KEY)

    # Load shloka data
    with open(DATA_DIR / 'gita_mvp.json', 'r', encoding='utf-8') as f:
        shlokas = json.load(f)
    lookup = {s['shloka_id']: s for s in shlokas}

    # Load existing interpretations
    interp_path = DATA_DIR / 'interpretations.json'
    with open(interp_path, 'r', encoding='utf-8') as f:
        interpretations = json.load(f)

    key_ids = get_key_shloka_ids()
    print(f"Regenerating {len(key_ids)} key shlokas...")

    success = 0
    failed = []

    for sid in key_ids:
        if sid not in lookup:
            print(f"  SKIP {sid} — not in shloka data")
            continue

        s = lookup[sid]
        prompt = PROMPT.format(sanskrit=s['sanskrit'], hindi_meaning=s['hindi_meaning'])

        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config={
                    'max_output_tokens': 500,
                    'temperature': 0.5,
                    'thinking_config': {'thinking_budget': 0},
                    'http_options': {'timeout': 15_000},
                },
            )
            text = response.text.strip()
            if text and '[SECTION]' in text:
                interpretations[sid] = text
                success += 1
                print(f"  OK {sid} ({len(text)} chars)")
            else:
                print(f"  WARN {sid} — no [SECTION] in response, skipping")
                failed.append(sid)
        except Exception as e:
            print(f"  ERROR {sid}: {e}")
            failed.append(sid)
            if '429' in str(e) or 'RESOURCE_EXHAUSTED' in str(e):
                print("  Rate limited, waiting 30s...")
                time.sleep(30)

        time.sleep(1)  # Rate limit spacing

    # Save updated interpretations
    with open(interp_path, 'w', encoding='utf-8') as f:
        json.dump(interpretations, f, ensure_ascii=False, indent=2)

    print(f"\nDone: {success}/{len(key_ids)} regenerated, {len(failed)} failed")
    if failed:
        print(f"Failed: {', '.join(failed)}")


if __name__ == '__main__':
    main()
