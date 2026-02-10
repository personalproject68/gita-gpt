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

कृपया ठीक तीन भाग लिखें, हर भाग को "[SECTION]" से अलग करें। सिर्फ content लिखें, कोई heading/label/prefix न लिखें।

भाग 1 — शब्दार्थ: मुख्य 4-6 संस्कृत शब्दों का हिंदी अर्थ, pipe से अलग।
भाग 2 — भावार्थ: श्लोक का सरल हिंदी सार (1-2 वाक्य)।
भाग 3 — मार्गदर्शन: व्यक्ति के प्रश्न "{user_query}" के संदर्भ में गीता की शिक्षा से सहज मार्गदर्शन (2-3 वाक्य)। टोन: शांत, सम्मानजनक। "आप" का प्रयोग।

उदाहरण output (इस format का पालन करें):
यदा यदा = जब-जब | धर्मस्य = धर्म की | ग्लानिः = हानि | सम्भवामि = प्रकट होता हूं[SECTION]जब-जब धर्म की हानि और अधर्म की वृद्धि होती है, तब-तब भगवान प्रकट होते हैं।[SECTION]आप जो कठिनाई अनुभव कर रहे हैं, वह स्थायी नहीं है। गीता कहती है कि बुरे समय में भी ईश्वर की व्यवस्था कार्य करती है। धैर्य रखें और अपना कर्म करते रहें।"""


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


def _ensure_three_sections(text: str, shloka: dict, prefetched: str) -> str:
    """Guarantee the response has exactly 3 [SECTION]-delimited parts.

    If Gemini returned malformed output, fall back to pre-fetched interpretation
    or construct a reasonable response from available data.
    """
    if not text:
        return prefetched or ''

    parts = text.split('[SECTION]')

    if len(parts) >= 3:
        # Good — Gemini followed instructions. Take first 3 parts only.
        return '[SECTION]'.join(p.strip() for p in parts[:3])

    # Gemini returned fewer than 3 sections — try to salvage
    # If pre-fetched has 3 sections, use it (it's reliable)
    if prefetched and len(prefetched.split('[SECTION]')) >= 3:
        return prefetched

    # Last resort: the text Gemini returned is probably shabdarth only.
    # Build a 3-part response from what we have.
    shabdarth = parts[0].strip() if parts else ''
    bhavarth = shloka.get('hindi_meaning', '')
    guidance = parts[1].strip() if len(parts) > 1 else ''

    return f"{shabdarth}[SECTION]{bhavarth}[SECTION]{guidance}"


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

    raw = _generate(client, prompt, max_tokens=1000)
    if not raw:
        return None

    # Get pre-fetched as fallback for missing sections
    prefetched = _INTERPRETATIONS.get(s['shloka_id'], '')
    return _ensure_three_sections(raw, s, prefetched)


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
