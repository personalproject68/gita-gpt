"""Shloka interpretation - pre-fetched (instant) + Gemini contextual (async follow-up)."""

import json
import logging
from config import DATA_DIR, GOOGLE_API_KEY

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


def get_contextual_interpretation(user_query: str, shlokas: list[dict]) -> str | None:
    """Generate broad Gita context and solutions from multiple shlokas.
    Returns Hindi interpretation (broad context + solution) or None on failure.
    """
    client = _get_gemini_client()
    if not client or not shlokas:
        return None

    # Prepare shlokas for prompt context
    shloka_context = ""
    for s in shlokas:
        # Use a summary or first part of commentary for more depth if available
        comm_excerpt = s.get('hindi_commentary', '')[:1500] 
        shloka_context += f"--- श्रीमद्भगवद्गीता {s['shloka_id']} ---\n"
        shloka_context += f"संस्कृत: {s['sanskrit']}\n"
        shloka_context += f"अर्थ (Meaning): {s['hindi_meaning']}\n"
        if comm_excerpt:
            shloka_context += f"व्याख्या (Detailed Commentary): {comm_excerpt}...\n"
        shloka_context += "\n"

    prompt = f"""आप श्रीमद्भगवद्गीता के एक अत्यंत सौम्य, गंभीर और सम्मानजनक मार्गदर्शक हैं। आपकी भाषा 'सुबोध' (सरल) है, लेकिन उसमें मर्यादा और ठहराव है। आप किसी विद्वान की तरह भारी शब्द नहीं बोलते, बल्कि एक ऐसे गहरे मित्र की तरह बात करते हैं जो जीवन के सार को बड़ी सरलता से समझा देता है।

एक व्यक्ति ने आपसे यह प्रश्न पूछा है:
"{user_query}"

उनके समाधान के लिए गीता के ये सूत्र उपलब्ध हैं:
{shloka_context}

कृपया एक मर्यादित और सरल संदेश लिखें (6-8 पंक्तियाँ):

1. **भाव को समझना (Respectful Acknowledgment):** बात की शुरुआत सम्मान के साथ करें। उन्हें महसूस कराएं कि आप उनके विचारों का आदर करते हैं। (उदा: "आपके मन के इस भाव को मैं समझ पा रहा हूँ...", "यह जीवन की एक स्वाभाविक स्थिति है...")।

2. **सरल और गहरा मर्म (Subodh Wisdom):** गीता के ज्ञान को 'सरल और सात्विक' हिंदी में समझाएं। 
   - **नियम:** बहुत कठिन शब्दों (सांख्य, निवृत्ति, द्वंद्व) से बचें।
   - **मर्यादा:** 'तू', 'बेटा', 'मम्मी-पापा' जैसे अत्यधिक अनौपचारिक शब्दों का प्रयोग **बिल्कुल न करें**। 'Hinglish' से बचें, शुद्ध लेकिन बोलचाल की 'सरल हिंदी' का प्रयोग करें। 
   - **शालीनता:** 'आसक्ति' की जगह 'मोह' या 'लगाव', 'अनित्य' की जगह 'परिवर्तनशील' जैसे शब्दों का प्रयोग करें जो सहज हों।

3. **आज का विचार (Contemplative Suggestion):** उन्हें कोई चंचल काम करने को न कहें। बल्कि एक गहरा विचार दें जिस पर वो मनन कर सकें (उदा: "आज केवल इस बात पर विचार करें कि परमात्मा सदैव आपके साथ हैं", "कुछ पल के लिए मौन रहकर अपनी सांसों पर ध्यान दें")।

निर्देश:
- संबोधन: "प्रिय आत्मन्" या "आदरणीय" (यदि उचित लगे)। हमेशा "आप" का प्रयोग करें।
- टोन: गंभीर (Mature), शांत (Calm) और गरिमापूर्ण (Dignified)।
- **बिल्कुल न लिखें:** श्लोक संख्या, संस्कृत शब्द, या कोई हेडिंग।"""

    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
            config={
                'max_output_tokens': 1000,
                'temperature': 0.7,
                'http_options': {'timeout': 15_000},
            },
        )
        text = response.text.strip()
        if text:
            logger.info(f"Broad context interpretation generated (Length: {len(text)})")
            return text
        return None
    except Exception as e:
        logger.error(f"Gemini contextual interpretation error: {e}")
        return None


def get_daily_interpretation(shloka: dict) -> str | None:
    """Generate a daily inspirational message based on a shloka for push notifications."""
    client = _get_gemini_client()
    if not client:
        return None

    shloka_context = f"--- श्रीमद्भगवद्गीता {shloka['shloka_id']} ---\n"
    shloka_context += f"संस्कृत: {shloka['sanskrit']}\n"
    shloka_context += f"अर्थ (Meaning): {shloka['hindi_meaning']}\n"
    if shloka.get('hindi_commentary'):
        shloka_context += f"व्याख्या: {shloka['hindi_commentary'][:1500]}...\n"

    prompt = f"""आप श्रीमद्भगवद्गीता के एक अत्यंत सौम्य, गंभीर और सम्मानजनक मार्गदर्शक हैं। आज के दिन के लिए आपको एक 'प्रेरणादायक विचार' (Thought of the Day) साझा करना है।

आज का श्लोक यह है:
{shloka_context}

कृपया एक मर्यादित और गरिमापूर्ण संदेश लिखें (5-6 पंक्तियाँ):

1. **आज का मंगल संदेश (Greeting/Context):** एक शांत और सकारात्मक शुरुआत करें। (उदा: "आज के इस पावन प्रभात पर...", "आज का दिन हमारे लिए एक नया अवसर है...")

2. **मर्म (Simple Wisdom):** इस श्लोक के सार को 'सरल और सात्विक' हिंदी में समझाएं। इसे ऐसे कहें कि सामने वाले को जीवन में एक दिशा मिले। 
   - **नियम:** 'तू', 'बेटा', 'Hinglish' या बहुत कठिन शब्दों का प्रयोग न करें। "आप" और सम्मानजनक भाषा का प्रयोग करें।

3. **आज का चिंतन (A Thought to Carry):** एक ऐसा विचार दें जिसे वो पूरे दिन अपने साथ रख सकें।

निर्देश:
- संबोधन: "प्रिय आत्मन्"
- टोन: गंभीर, शांत और प्रेरक।
- **बिल्कुल न लिखें:** श्लोक संख्या, संस्कृत शब्द, या कोई हेडिंग।"""

    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
            config={
                'max_output_tokens': 500,
                'temperature': 0.7,
                'http_options': {'timeout': 15_000},
            },
        )
        text = response.text.strip()
        if text:
            logger.info(f"Daily interpretation generated for {shloka['shloka_id']}")
            return text
        return None
    except Exception as e:
        logger.error(f"Gemini daily interpretation error: {e}")
        return None
