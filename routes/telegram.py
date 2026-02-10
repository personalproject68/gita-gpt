"""Telegram webhook handler - core bot logic."""

import logging
import tempfile
from collections import deque

from flask import Blueprint, request, jsonify

from config import TOPIC_MENU, ADMIN_USER_ID
from services.telegram_api import send_message, send_chat_action, answer_callback_query, get_file, download_file, make_inline_keyboard
from services.search import find_relevant_shlokas
from services.ai_interpretation import (
    get_ai_interpretation, get_contextual_interpretation,
)
from services.session import get_session, save_session, update_context, update_top_topics
from services.formatter import (
    format_shloka_list, format_welcome, format_help,
    format_topic_keyboard, format_shloka,
    format_rate_limit, format_content_blocked, format_invalid_input,
    format_amrit_menu, format_amrit_shloka,
)
from models.shloka import CURATED_TOPICS, SHLOKA_LOOKUP, COMPLETE_LOOKUP
from services.voice import transcribe_voice
from services.daily import subscribe, unsubscribe, get_journey_position, advance_journey, send_journey_shloka
from services.metrics import get_daily_stats
from guardrails.rate_limiter import check_rate_limit
from guardrails.content_filter import check_content
from guardrails.sanitizer import sanitize_input, is_valid_input

logger = logging.getLogger('gitagpt.telegram')

bp = Blueprint('telegram', __name__)

# Deduplication: track recent update_ids to prevent Telegram retry duplicates
_recent_updates = deque(maxlen=100)


def _reply(chat_id, text, reply_markup=None):
    """Helper to send reply."""
    send_message(chat_id, text, reply_markup)


# ============ Webhook Route ============

@bp.route('/webhook', methods=['POST'])
def telegram_webhook():
    """Receive Telegram updates via webhook."""
    data = request.get_json(force=True)

    # Deduplicate: skip if we already processed this update
    update_id = data.get('update_id')
    if update_id in _recent_updates:
        logger.info(f"Skipping duplicate update_id={update_id}")
        return jsonify({'ok': True})
    if update_id:
        _recent_updates.append(update_id)

    try:
        if 'callback_query' in data:
            _handle_callback(data['callback_query'])
        elif 'message' in data:
            msg = data['message']
            chat_id = msg['chat']['id']

            if 'voice' in msg:
                _handle_voice(chat_id, msg['voice'])
            elif 'text' in msg:
                text = msg['text'].strip()
                if text.startswith('/'):
                    _handle_command(chat_id, text)
                else:
                    _handle_text(chat_id, text)

        return jsonify({'ok': True})

    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
        return jsonify({'ok': True})  # Always return 200 to Telegram


# ============ Command Handlers ============

def _handle_command(chat_id, text):
    """Handle /commands."""
    user_id = str(chat_id)
    cmd = text.split()[0].lower().split('@')[0]  # Handle /start@BotName

    if cmd == '/start':
        subscribe(user_id)
        _reply(chat_id, format_welcome())

    elif cmd == '/help':
        _reply(chat_id, format_help())

    elif cmd == '/topic':
        update_context(user_id, 'topic_menu')
        text, keyboard = format_topic_keyboard()
        _reply(chat_id, text, keyboard)

    elif cmd == '/daily':
        send_chat_action(chat_id, 'typing')
        position = get_journey_position(user_id)
        message, markup = send_journey_shloka(user_id, position)
        _reply(chat_id, message, markup)

    elif cmd == '/amrit':
        text, keyboard = format_amrit_menu()
        _reply(chat_id, text, keyboard)

    elif cmd == '/stats':
        if user_id != ADMIN_USER_ID:
            _reply(chat_id, format_help())
            return
        stats = get_daily_stats()
        if stats:
            text = (
                f"📊 Gita Sarathi Stats — {stats['date']}\n\n"
                f"👥 DAU yesterday: {stats['dau']}\n"
                f"🆕 New users: {stats['new_users']}\n"
                f"💬 Messages: {stats['total_messages']}\n"
                f"📨 Active subscribers: {stats['active_subscribers']}\n"
                f"❌ API failures: {stats['api_failures']}"
            )
        else:
            text = "Stats unavailable. Check logs."
        _reply(chat_id, text)

    else:
        _reply(chat_id, format_help())


# ============ Text Handler ============

def _handle_text(chat_id, message):
    """Handle all text messages."""
    user_id = str(chat_id)

    # Rate limit
    if not check_rate_limit(user_id):
        _reply(chat_id, format_rate_limit())
        return

    # Sanitize
    message = sanitize_input(message)
    if not is_valid_input(message):
        _reply(chat_id, format_invalid_input())
        return

    # Content filter
    is_ok, reason = check_content(message)
    if not is_ok:
        _reply(chat_id, format_content_blocked(reason))
        return

    msg_lower = message.lower().strip()

    # Text-based command shortcuts
    if msg_lower in ['hi', 'hello', 'नमस्ते', 'हेलो', 'start']:
        subscribe(user_id)
        _reply(chat_id, format_welcome())
        return

    if msg_lower in ['help', 'मदद', '?', 'सहायता']:
        _reply(chat_id, format_help())
        return

    if msg_lower in ['topic', 'topics', 'विषय', 'विषयों']:
        update_context(user_id, 'topic_menu')
        text, keyboard = format_topic_keyboard()
        _reply(chat_id, text, keyboard)
        return

    if msg_lower in ['daily', 'आज का श्लोक', 'प्रेरणा', 'aaj', 'आज']:
        send_chat_action(chat_id, 'typing')
        position = get_journey_position(user_id)
        message, markup = send_journey_shloka(user_id, position)
        _reply(chat_id, message, markup)
        return

    if msg_lower in ['अमृत', 'amrit', 'प्रसिद्ध', 'famous']:
        text, keyboard = format_amrit_menu()
        _reply(chat_id, text, keyboard)
        return

    if msg_lower in ['और', 'more', 'aur', 'next']:
        _handle_more(chat_id, user_id)
        return

    if msg_lower in ['रोकें', 'stop', 'unsubscribe', 'रुकें']:
        unsubscribe(user_id)
        _reply(chat_id, "🙏 आपको अब रोज़ाना श्लोक नहीं मिलेगा।\n\nदोबारा शुरू करने के लिए /start भेजें।")
        return

    # Process as question
    _process_question(chat_id, user_id, message)


def _handle_more(chat_id, user_id):
    """Handle 'और' / 'more' - show next related shloka."""
    session = get_session(user_id)
    last_query = session.get('last_query', '')
    last_shlokas = session.get('last_shlokas', [])

    if not last_query:
        _reply(chat_id, "🙏 पहले कोई प्रश्न पूछें, फिर 'और' भेजें अगला श्लोक देखने के लिए।")
        return

    shown_ids = {s['shloka_id'] for s in last_shlokas}
    all_results = find_relevant_shlokas(last_query, max_results=5)
    new_results = [s for s in all_results if s['shloka_id'] not in shown_ids]

    if not new_results:
        _reply(chat_id, "🙏 इस विषय पर और श्लोक उपलब्ध नहीं हैं।\n\nनया प्रश्न पूछें या /topic भेजें।")
        return

    shloka = new_results[0]
    all_shown = last_shlokas + [shloka]
    save_session(user_id, last_query, all_shown)

    interpretation = get_ai_interpretation(last_query, [shloka])
    _reply(chat_id, format_shloka(shloka, interpretation))


# ============ Callback Query Handler (Topic Buttons) ============

def _handle_callback(callback_query):
    """Handle inline keyboard button clicks — instant using curated topics."""
    cb_id = callback_query['id']
    data = callback_query.get('data', '')
    chat_id = callback_query['message']['chat']['id']
    user_id = str(chat_id)

    answer_callback_query(cb_id)

    # Journey: "अगला श्लोक →" button
    if data == 'journey:next':
        logger.info(f"Journey advance by {user_id}")
        send_chat_action(chat_id, 'typing')
        new_pos = advance_journey(user_id)
        message, markup = send_journey_shloka(user_id, new_pos)
        _reply(chat_id, message, markup)
        return

    # अमृत श्लोक: back to menu or show specific shloka
    if data == 'amrit:back':
        text, keyboard = format_amrit_menu()
        _reply(chat_id, text, keyboard)
        return

    if data.startswith('amrit:'):
        shloka_id = data.split(':', 1)[1]
        shloka = COMPLETE_LOOKUP.get(shloka_id)
        if not shloka:
            _reply(chat_id, "श्लोक नहीं मिला।")
            return
        logger.info(f"Amrit shloka: {shloka_id} by {user_id}")
        send_chat_action(chat_id, 'typing')
        interpretation = get_ai_interpretation("", [shloka])
        response = format_amrit_shloka(shloka, interpretation)
        back_button = make_inline_keyboard([[{'text': '← अमृत श्लोक', 'callback_data': 'amrit:back'}]])
        _reply(chat_id, response, back_button)
        return

    if not data.startswith('topic:'):
        return

    topic_id = data.split(':', 1)[1]
    if topic_id not in TOPIC_MENU:
        return

    logger.info(f"Topic: {topic_id} by {user_id}")
    update_context(user_id, None)
    update_top_topics(user_id, topic_id)

    # Direct lookup from curated topics (instant — no Cohere search)
    topic_label = TOPIC_MENU[topic_id]
    if topic_id in CURATED_TOPICS:
        best_ids = CURATED_TOPICS[topic_id].get('best_shlokas', [])
        shlokas = [SHLOKA_LOOKUP[sid] for sid in best_ids[:3] if sid in SHLOKA_LOOKUP]
    else:
        shlokas = find_relevant_shlokas(topic_label, max_results=3)

    save_session(user_id, topic_label, shlokas)

    send_chat_action(chat_id, 'typing')
    interpretation = get_contextual_interpretation(topic_label, shlokas) if shlokas else ""
    if not interpretation:
        interpretation = get_ai_interpretation(topic_label, shlokas[:1])
    response = format_shloka_list(shlokas, interpretation)
    if len(shlokas) > 1:
        response += "\n\n👉 'और' भेजें अगला श्लोक देखने के लिए"
    _reply(chat_id, response)


# ============ Voice Handler ============

def _handle_voice(chat_id, voice):
    """Handle voice messages."""
    user_id = str(chat_id)

    if not check_rate_limit(user_id):
        _reply(chat_id, format_rate_limit())
        return

    _reply(chat_id, "🎙️ आपकी आवाज़ सुन रहा हूं...")

    try:
        file_info = get_file(voice['file_id'])
        if not file_info:
            _reply(chat_id, "🙏 आवाज़ प्रोसेस नहीं हो पाई। कृपया लिखकर भेजें।")
            return

        file_data = download_file(file_info['file_path'])
        if not file_data:
            _reply(chat_id, "🙏 आवाज़ डाउनलोड नहीं हो पाई। कृपया लिखकर भेजें।")
            return

        with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as tmp:
            tmp.write(file_data)
            tmp_path = tmp.name

        transcript = transcribe_voice(tmp_path)

        if not transcript:
            _reply(chat_id, "🙏 आवाज़ समझ नहीं आई। कृपया दोबारा बोलें या लिखकर भेजें।")
            return

        _reply(chat_id, f"🎙️ आपने कहा: \"{transcript}\"")
        _process_question(chat_id, user_id, transcript)

    except Exception as e:
        logger.error(f"Voice error: {e}", exc_info=True)
        _reply(chat_id, "🙏 आवाज़ प्रोसेस नहीं हो पाई। कृपया लिखकर भेजें।")


# ============ Core Question Processing ============

def _process_question(chat_id, user_id: str, query: str):
    """Search shlokas and send single contextual response."""
    update_context(user_id, None)

    send_chat_action(chat_id, 'typing')

    shlokas = find_relevant_shlokas(query, max_results=3)
    save_session(user_id, query, shlokas)

    if not shlokas:
        _reply(chat_id, "क्षमा करें, इस विषय पर कोई उपयुक्त श्लोक नहीं मिला। कृपया अलग शब्दों में पूछें।")
        return

    send_chat_action(chat_id, 'typing')

    # Contextual Gemini interpretation (synchronous), fallback to pre-fetched
    interpretation = get_contextual_interpretation(query, shlokas)
    if not interpretation:
        interpretation = get_ai_interpretation(query, shlokas[:1])

    response = format_shloka(shlokas[0], interpretation)
    if len(shlokas) > 1:
        response += "\n\n👉 'और' भेजें अगला श्लोक देखने के लिए"
    _reply(chat_id, response)
