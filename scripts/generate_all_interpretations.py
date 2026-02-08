"""Batch-generate interpretations for all 701 shlokas using Gemini."""

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import DATA_DIR, GOOGLE_API_KEY

COMPLETE_PATH = DATA_DIR / 'raw' / 'gita_complete.json'
INTERP_PATH = DATA_DIR / 'interpretations.json'

PROMPT = """आप श्रीमद्भगवद्गीता के विद्वान हैं। केवल नीचे दिए गए एक श्लोक के लिए output दें। किसी अन्य श्लोक का उल्लेख न करें।

श्लोक:
{sanskrit}

अर्थ: {hindi_meaning}

कृपया ठीक तीन भाग लिखें, हर भाग को "[SECTION]" से अलग करें:

भाग 1 — शब्दार्थ (1 पंक्ति): केवल इस श्लोक के मुख्य संस्कृत शब्दों का हिंदी अर्थ, pipe (|) से अलग।
उदाहरण: यदा यदा = जब-जब | धर्मस्य = धर्म की | ग्लानिः = हानि

भाग 2 — भावार्थ (1-2 वाक्य): श्लोक का सरल हिंदी अर्थ। शुद्ध सरल हिंदी।

भाग 3 — आज का चिंतन (2-3 वाक्य): इस श्लोक से जुड़ा एक प्रेरणादायक विचार जो पूरे दिन साथ रहे।
टोन: शांत, सम्मानजनक, प्रेरक। "आप" का प्रयोग। Hinglish/अंग्रेज़ी से बचें।

बिल्कुल न लिखें: कोई heading, label, श्लोक संख्या, "शब्दार्थ:", "भावार्थ:" जैसे prefix, या कोई अन्य श्लोक।
सिर्फ content लिखें, [SECTION] से अलग करें। संक्षिप्त रखें।"""

MODELS = ['gemini-2.5-flash', 'gemini-2.5-flash-lite']


def generate(client, shloka: dict) -> str | None:
    """Generate interpretation for a single shloka."""
    prompt = PROMPT.format(
        sanskrit=shloka['sanskrit'],
        hindi_meaning=shloka['hindi_meaning'],
    )
    for model in MODELS:
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config={
                    'max_output_tokens': 1000,
                    'temperature': 0.7,
                    'thinking_config': {'thinking_budget': 0},
                    'http_options': {'timeout': 30_000},
                },
            )
            text = response.text.strip()
            if text:
                return text
        except Exception as e:
            if '429' in str(e) or 'RESOURCE_EXHAUSTED' in str(e):
                print(f"  {model} rate limited, trying fallback...")
                continue
            print(f"  Error ({model}): {e}")
            return None
    return None


def main():
    if not GOOGLE_API_KEY:
        print("ERROR: GOOGLE_API_KEY not set")
        sys.exit(1)

    from google import genai
    client = genai.Client(api_key=GOOGLE_API_KEY)

    # Load shlokas
    with open(COMPLETE_PATH, 'r', encoding='utf-8') as f:
        shlokas = json.load(f)
    print(f"Loaded {len(shlokas)} shlokas")

    # Load existing interpretations
    if INTERP_PATH.exists():
        with open(INTERP_PATH, 'r', encoding='utf-8') as f:
            interpretations = json.load(f)
    else:
        interpretations = {}

    existing = sum(1 for v in interpretations.values() if v.strip())
    print(f"Existing non-empty interpretations: {existing}")

    # Generate missing
    missing = [s for s in shlokas if not interpretations.get(s['shloka_id'], '').strip()]
    print(f"Missing: {len(missing)}")

    generated = 0
    failed = 0
    for i, shloka in enumerate(missing):
        sid = shloka['shloka_id']
        print(f"[{i+1}/{len(missing)}] Generating {sid}...", end=' ')

        result = generate(client, shloka)
        if result:
            interpretations[sid] = result
            generated += 1
            print(f"OK ({len(result)} chars)")
        else:
            failed += 1
            print("FAILED")

        # Save periodically
        if (i + 1) % 20 == 0:
            with open(INTERP_PATH, 'w', encoding='utf-8') as f:
                json.dump(interpretations, f, ensure_ascii=False, indent=2)
            print(f"  Saved. Generated: {generated}, Failed: {failed}")

        # Rate limit: ~4 requests/sec for free tier
        time.sleep(0.3)

    # Final save
    with open(INTERP_PATH, 'w', encoding='utf-8') as f:
        json.dump(interpretations, f, ensure_ascii=False, indent=2)

    total_filled = sum(1 for v in interpretations.values() if v.strip())
    print(f"\nDone! Generated: {generated}, Failed: {failed}")
    print(f"Total interpretations: {total_filled}/701")


if __name__ == '__main__':
    main()
