"""Shloka interpretation - pre-fetched (instant) + Gemini contextual (async follow-up)."""

import json
import logging
from config import DATA_DIR, GOOGLE_API_KEY
from services.metrics import log_event

logger = logging.getLogger('gitagpt.interpretation')

# Load pre-fetched interpretations at startup
_INTERPRETATIONS = {}
_interp_path = DATA_DIR / 'interpretations.json'
if _interp_path.exists():
    with open(_interp_path, 'r', encoding='utf-8') as f:
        _INTERPRETATIONS = json.load(f)
    logger.info(f"Loaded {len(_INTERPRETATIONS)} pre-fetched interpretations")


def get_ai_interpretation(user_query: str, shlokas: list[dict]) -> str:
    """Get interpretation for the first shloka. Instant - no API call."""
    if not shlokas:
        return ""

    shloka_id = shlokas[0]['shloka_id']
    return _INTERPRETATIONS.get(shloka_id, "")


# --- Gemini contextual interpretation (Phase 2) ---

_gemini_client = None
_MODELS = ['gemini-2.5-flash', 'gemini-2.5-flash-lite']


def _get_gemini_client():
    """Lazy-init Gemini client. Returns None if unavailable."""
    global _gemini_client
    if _gemini_client is not None:
        return _gemini_client
    if not GOOGLE_API_KEY:
        logger.warning("GOOGLE_API_KEY not set, contextual interpretation disabled")
        return None
    try:
        from google import genai
        _gemini_client = genai.Client(api_key=GOOGLE_API_KEY)
        logger.info("Gemini client initialized for contextual interpretation")
        return _gemini_client
    except Exception as e:
        logger.error(f"Gemini init error: {e}")
        return None


def _generate(client, prompt: str, max_tokens: int) -> str | None:
    """Call Gemini with automatic fallback on quota exhaustion."""
    for model in _MODELS:
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config={
                    'max_output_tokens': max_tokens,
                    'temperature': 0.7,
                    'thinking_config': {'thinking_budget': 0},
                    'http_options': {'timeout': 15_000},
                },
            )
            text = response.text.strip()
            if text:
                logger.info(f"Generated via {model} (Length: {len(text)})")
                return text
        except Exception as e:
            if '429' in str(e) or 'RESOURCE_EXHAUSTED' in str(e):
                log_event('api_error', data=f'gemini_429_{model}')
                logger.warning(f"{model} quota exhausted, trying fallback...")
                continue
            log_event('api_error', data=f'gemini_error_{model}')
            logger.error(f"Gemini error ({model}): {e}")
            return None
    log_event('api_error', data='gemini_all_exhausted')
    return None


_SHABDARTH_PROMPT = """आप श्रीमद्भगवद्गीता के विद्वान हैं। केवल नीचे दिए गए एक श्लोक के लिए output दें। किसी अन्य श्लोक का उल्लेख न करें।

श्लोक:
{sanskrit}

अर्थ: {hindi_meaning}
व्यक्ति का प्रश्न: "{user_query}"

कृपया ठीक तीन भाग लिखें, हर भाग को "[SECTION]" से अलग करें:

भाग 1 — शब्दार्थ (1 पंक्ति): केवल इस श्लोक के मुख्य संस्कृत शब्दों का हिंदी अर्थ, pipe (|) से अलग।
उदाहरण: यदा यदा = जब-जब | धर्मस्य = धर्म की | ग्लानिः = हानि

भाग 2 — भावार्थ (1-2 वाक्य): श्लोक का सरल हिंदी अर्थ। शुद्ध सरल हिंदी।

भाग 3 — मार्गदर्शन (2-3 वाक्य): व्यक्ति के प्रश्न के संदर्भ में गीता की शिक्षा से सहज मार्गदर्शन।
टोन: शांत, सम्मानजनक। "आप" का प्रयोग। Hinglish/अंग्रेज़ी से बचें।

बिल्कुल न लिखें: कोई heading, label, श्लोक संख्या, "शब्दार्थ:", "भावार्थ:" जैसे prefix, या कोई अन्य श्लोक।
सिर्फ content लिखें, [SECTION] से अलग करें। संक्षिप्त रखें।"""


_DAILY_PROMPT = """आप श्रीमद्भगवद्गीता के विद्वान हैं। केवल नीचे दिए गए एक श्लोक के लिए output दें। किसी अन्य श्लोक का उल्लेख न करें।

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


def get_contextual_interpretation(user_query: str, shlokas: list[dict]) -> str | None:
    """Generate shabdarth + bhavarth + contextual guidance for user's question."""
    client = _get_gemini_client()
    if not client or not shlokas:
        return None

    s = shlokas[0]
    prompt = _SHABDARTH_PROMPT.format(
        sanskrit=s['sanskrit'],
        hindi_meaning=s['hindi_meaning'],
        user_query=user_query,
    )

    return _generate(client, prompt, max_tokens=1000)


def get_daily_interpretation(shloka: dict) -> str | None:
    """Generate shabdarth + bhavarth + daily thought for push notifications."""
    client = _get_gemini_client()
    if not client:
        return None

    prompt = _DAILY_PROMPT.format(
        sanskrit=shloka['sanskrit'],
        hindi_meaning=shloka['hindi_meaning'],
    )

    return _generate(client, prompt, max_tokens=1000)
