"""Telegram response formatting - forward-friendly."""

import re
from datetime import datetime
from config import TOPIC_MENU, AMRIT_SHLOKAS
from services.telegram_api import make_inline_keyboard


def _strip_verse_ref(text: str) -> str:
    """Strip ।।X.Y।। or ।।X.Y -- X.Z।। verse reference prefixes and व्याख्या-- labels."""
    if not text:
        return text
    text = re.sub(r'^[।॥\s]*\d+\.\d+(\s*[-—–]+\s*\d+\.\d+)?[।॥\s]*', '', text).strip()
    text = re.sub(r'^व्याख्या\s*[-—–]+\s*', '', text).strip()
    return text


def _trim_commentary(text: str, max_len: int = 300) -> str:
    """Trim commentary to max_len, cutting at last sentence boundary."""
    if not text or len(text) <= max_len:
        return text
    trimmed = text[:max_len]
    # Cut at last sentence-ending punctuation
    for sep in ['।', '|', '.', '॥']:
        idx = trimmed.rfind(sep)
        if idx > 50:
            return trimmed[:idx + 1]
    return trimmed.rstrip() + '…'


def _parse_interpretation(interpretation: str) -> tuple[str, str, str]:
    """Parse Gemini's [SECTION] separated output into (shabdarth, bhavarth, guidance).
    If no [SECTION] found (pre-fetched), treat as bhavarth only."""
    if not interpretation:
        return "", "", ""

    if '[SECTION]' not in interpretation:
        # Pre-fetched interpretation — use as bhavarth, skip shabdarth
        return "", _strip_verse_ref(interpretation), ""

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
        parts.extend(["", _strip_verse_ref(shloka['hindi_meaning'])])

    commentary = _strip_verse_ref(shloka.get('hindi_commentary', ''))
    if commentary:
        parts.extend(["", f"📜 {_trim_commentary(commentary)}"])

    if guidance:
        parts.extend(["", f"💭 {guidance}"])

    parts.extend(["", "— गीता सारथी 🙏"])

    return '\n'.join(parts)


def format_shloka_list(shlokas: list[dict], interpretation: str = "") -> str:
    """Format response with shlokas + interpretation."""
    if not shlokas:
        return "क्षमा करें, इस विषय पर कोई उपयुक्त श्लोक नहीं मिला। कृपया अलग शब्दों में पूछें।"

    return format_shloka(shlokas[0], interpretation)


def format_welcome() -> str:
    return """🙏 नमस्ते! गीता सारथी में आपका स्वागत है।

मैं भगवद्गीता के ज्ञान से आपके जीवन के प्रश्नों का उत्तर देता हूं।

📝 आप पूछ सकते हैं:
• "मुझे गुस्सा बहुत आता है"
• "जीवन में शांति कैसे मिले?"
• "कर्म क्या है?"

📚 विषय देखने के लिए /topic भेजें
🌅 आज का श्लोक: /daily
📿 प्रसिद्ध श्लोक: /amrit

अपना प्रश्न हिंदी या English में पूछें... 🙏"""


def format_help() -> str:
    return """🙏 गीता सारथी - सहायता

📝 आप क्या कर सकते हैं:

• कोई भी प्रश्न पूछें
  "मुझे गुस्सा आता है"
  "मन शांत कैसे करें"

• /topic या विषय — विषयों की सूची
• /daily या प्रेरणा — आज का श्लोक
• /amrit या अमृत — प्रसिद्ध श्लोक
• और — अगला संबंधित श्लोक
• रोकें — दैनिक श्लोक बंद करें

— गीता सारथी 🙏"""


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
        parts.extend(["", _strip_verse_ref(shloka['hindi_meaning'])])

    commentary = _strip_verse_ref(shloka.get('hindi_commentary', ''))
    if commentary:
        parts.extend(["", f"📜 {_trim_commentary(commentary)}"])

    if guidance:
        parts.extend(["", f"💭 {guidance}"])

    parts.extend(["", "— गीता सारथी 🙏"])

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


def format_journey_shloka(shloka: dict, interpretation: str, position: int, total: int = 701, chapter_name: str = "") -> str:
    """Format a journey shloka with progress line."""
    shabdarth, bhavarth, guidance = _parse_interpretation(interpretation)

    chapter = shloka.get('chapter', '')
    parts = [
        f"📿 गीता यात्रा — श्लोक {position + 1}/{total}",
        f"अध्याय {chapter} — {chapter_name}",
        "",
        shloka['sanskrit'],
    ]

    if shabdarth:
        parts.extend(["", f"📖 {shabdarth}"])

    if bhavarth:
        parts.extend(["", bhavarth])
    else:
        parts.extend(["", _strip_verse_ref(shloka['hindi_meaning'])])

    commentary = _strip_verse_ref(shloka.get('hindi_commentary', ''))
    if commentary:
        parts.extend(["", f"📜 {_trim_commentary(commentary)}"])

    if guidance:
        parts.extend(["", f"💭 {guidance}"])

    parts.extend(["", "— गीता सारथी 🙏"])

    return '\n'.join(parts)


def format_chapter_milestone(chapter: int, chapter_name: str, position: int, total: int, next_chapter: int, next_chapter_name: str) -> str:
    """Format chapter completion celebration."""
    parts = [f"🎉 अध्याय {chapter} पूर्ण! ({chapter_name})"]
    parts.append(f"आपने {position + 1}/{total} श्लोक पढ़े।")
    if next_chapter <= 18 and next_chapter_name:
        parts.append(f"अगला: अध्याय {next_chapter} — {next_chapter_name}")
    return '\n'.join(parts)


def format_journey_complete() -> str:
    """Format journey completion congratulation."""
    return """🎉 बधाई हो! आपने सम्पूर्ण श्रीमद्भगवद्गीता की यात्रा पूर्ण की!

📿 701 श्लोक — 18 अध्याय

गीता का ज्ञान सदा आपके साथ रहे। 🙏

— गीता सारथी 🙏"""


def format_amrit_menu() -> tuple[str, dict]:
    """Return अमृत श्लोक menu text + inline keyboard markup."""
    text = "📿 अमृत श्लोक — गीता के सबसे प्रसिद्ध श्लोक\n\nनीचे बटन दबाएं 👇"

    buttons = []
    for shloka_id, label in AMRIT_SHLOKAS:
        buttons.append([{'text': f"गीता {shloka_id} — {label}", 'callback_data': f'amrit:{shloka_id}'}])

    keyboard = make_inline_keyboard(buttons)
    return text, keyboard


def format_amrit_shloka(shloka: dict, interpretation: str = "") -> str:
    """Format an amrit shloka response."""
    shabdarth, bhavarth, guidance = _parse_interpretation(interpretation)

    parts = [
        f"📿 अमृत श्लोक — गीता {shloka['shloka_id']}",
        "",
        shloka['sanskrit'],
    ]

    if shabdarth:
        parts.extend(["", f"📖 {shabdarth}"])

    if bhavarth:
        parts.extend(["", bhavarth])
    else:
        parts.extend(["", _strip_verse_ref(shloka['hindi_meaning'])])

    commentary = _strip_verse_ref(shloka.get('hindi_commentary', ''))
    if commentary:
        parts.extend(["", f"📜 {_trim_commentary(commentary)}"])

    if guidance:
        parts.extend(["", f"💭 {guidance}"])

    parts.extend(["", "— गीता सारथी 🙏"])

    return '\n'.join(parts)
