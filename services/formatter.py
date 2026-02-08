"""Telegram response formatting - forward-friendly."""

from datetime import datetime
from config import TOPIC_MENU
from services.telegram_api import make_inline_keyboard


def _parse_interpretation(interpretation: str) -> tuple[str, str, str]:
    """Parse Gemini's --- separated output into (shabdarth, bhavarth, guidance).
    Returns empty strings for missing parts."""
    if not interpretation:
        return "", "", ""

    parts = [p.strip() for p in interpretation.split('[SECTION]')]
    shabdarth = parts[0] if len(parts) > 0 else ""
    bhavarth = parts[1] if len(parts) > 1 else ""
    guidance = parts[2] if len(parts) > 2 else ""
    return shabdarth, bhavarth, guidance


def format_shloka(shloka: dict, interpretation: str = "") -> str:
    """Format a single shloka for Telegram with shabdarth + bhavarth + guidance."""
    shabdarth, bhavarth, guidance = _parse_interpretation(interpretation)

    parts = [
        f"📿 गीता {shloka['shloka_id']}",
        "",
        shloka['sanskrit'],
    ]

    if shabdarth:
        parts.extend(["", f"📖 {shabdarth}"])

    if bhavarth:
        parts.extend(["", bhavarth])
    else:
        parts.extend(["", shloka['hindi_meaning']])

    if guidance:
        parts.extend(["", f"💭 {guidance}"])

    parts.extend(["", "— गीता GPT 🙏"])

    return '\n'.join(parts)


def format_shloka_list(shlokas: list[dict], interpretation: str = "") -> str:
    """Format response with shlokas + interpretation."""
    if not shlokas:
        return "क्षमा करें, इस विषय पर कोई उपयुक्त श्लोक नहीं मिला। कृपया अलग शब्दों में पूछें।"

    return format_shloka(shlokas[0], interpretation)


def format_welcome() -> str:
    return """🙏 नमस्ते! गीता GPT में आपका स्वागत है।

मैं भगवद्गीता के ज्ञान से आपके जीवन के प्रश्नों का उत्तर देता हूं।

📝 आप पूछ सकते हैं:
• "मुझे गुस्सा बहुत आता है"
• "जीवन में शांति कैसे मिले?"
• "कर्म क्या है?"

📚 विषय देखने के लिए /topic भेजें
🌅 आज का श्लोक: /daily

अपना प्रश्न हिंदी या English में पूछें... 🙏"""


def format_help() -> str:
    return """🙏 गीता GPT - सहायता

📝 आप क्या कर सकते हैं:

• कोई भी प्रश्न पूछें
  "मुझे गुस्सा आता है"
  "मन शांत कैसे करें"

• /topic या विषय — विषयों की सूची
• /daily या प्रेरणा — आज का श्लोक
• और — अगला संबंधित श्लोक
• रोकें — दैनिक श्लोक बंद करें

— गीता GPT 🙏"""


def format_topic_keyboard() -> tuple[str, dict]:
    """Return topic menu text + inline keyboard markup dict."""
    text = "📚 अपना विषय चुनें:\n\nनीचे बटन दबाएं 👇"

    buttons = []
    for topic_id, label in TOPIC_MENU.items():
        buttons.append([{'text': label, 'callback_data': f'topic:{topic_id}'}])

    keyboard = make_inline_keyboard(buttons)
    return text, keyboard


def format_daily_shloka(shloka: dict, interpretation: str = "") -> str:
    days_hi = ['सोमवार', 'मंगलवार', 'बुधवार', 'गुरुवार', 'शुक्रवार', 'शनिवार', 'रविवार']
    day_name = days_hi[datetime.now().weekday()]

    shabdarth, bhavarth, guidance = _parse_interpretation(interpretation)

    parts = [
        f"🌅 {day_name} का गीता प्रेरणा",
        "",
        f"📿 गीता {shloka['shloka_id']}",
        "",
        shloka['sanskrit'],
    ]

    if shabdarth:
        parts.extend(["", f"📖 {shabdarth}"])

    if bhavarth:
        parts.extend(["", bhavarth])
    else:
        parts.extend(["", shloka['hindi_meaning']])

    if guidance:
        parts.extend(["", f"💭 {guidance}"])

    parts.extend(["", "— गीता GPT 🙏"])

    return '\n'.join(parts)


def format_rate_limit() -> str:
    return "🙏 कृपया थोड़ा रुकें। आप बहुत तेज़ी से संदेश भेज रहे हैं।\n\nकुछ देर बाद फिर प्रयास करें।"


def format_content_blocked(reason: str) -> str:
    if reason == 'profanity':
        return "🙏 आपके मन में कुछ कठिन भाव हैं। क्या मैं गीता का मार्गदर्शन दूं?\n\nकृपया अपना प्रश्न अलग शब्दों में पूछें।"
    elif reason == 'manipulation':
        return "🙏 मैं केवल गीता के ज्ञान से उत्तर देता हूं।\n\nकृपया जीवन से जुड़ा प्रश्न पूछें।"
    else:
        return "🙏 कृपया गीता से संबंधित प्रश्न पूछें।\n\nजैसे: मन की शांति, कर्म, भय, क्रोध आदि।"


def format_invalid_input() -> str:
    return "🙏 कृपया अपना प्रश्न लिखें।\n\nमदद के लिए /help भेजें।"
