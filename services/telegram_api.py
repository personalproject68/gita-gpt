"""Lightweight Telegram Bot API wrapper using requests."""

import json
import logging
import requests
from config import TELEGRAM_BOT_TOKEN

logger = logging.getLogger('gitagpt.telegram_api')

BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}" if TELEGRAM_BOT_TOKEN else ""


def send_message(chat_id, text, reply_markup=None):
    """Send a text message to a chat."""
    payload = {
        'chat_id': chat_id,
        'text': text,
    }
    if reply_markup:
        payload['reply_markup'] = json.dumps(reply_markup)

    try:
        resp = requests.post(f"{BASE_URL}/sendMessage", json=payload, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error(f"sendMessage error: {e}")
        return None


def send_chat_action(chat_id, action='typing'):
    """Send chat action (e.g. typing indicator) to a chat."""
    try:
        requests.post(
            f"{BASE_URL}/sendChatAction",
            json={'chat_id': chat_id, 'action': action},
            timeout=5,
        )
    except Exception as e:
        logger.error(f"sendChatAction error: {e}")


def answer_callback_query(callback_query_id, text=None):
    """Answer a callback query (button click)."""
    payload = {'callback_query_id': callback_query_id}
    if text:
        payload['text'] = text
    try:
        requests.post(f"{BASE_URL}/answerCallbackQuery", json=payload, timeout=5)
    except Exception as e:
        logger.error(f"answerCallbackQuery error: {e}")


def get_file(file_id) -> dict | None:
    """Get file info for downloading."""
    try:
        resp = requests.post(f"{BASE_URL}/getFile", json={'file_id': file_id}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get('ok'):
            return data['result']
    except Exception as e:
        logger.error(f"getFile error: {e}")
    return None


def download_file(file_path) -> bytes | None:
    """Download a file from Telegram servers."""
    try:
        url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}"
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return resp.content
    except Exception as e:
        logger.error(f"download_file error: {e}")
    return None


def set_webhook(url):
    """Set webhook URL for the bot."""
    try:
        resp = requests.post(f"{BASE_URL}/setWebhook", json={'url': url}, timeout=10)
        return resp.json()
    except Exception as e:
        logger.error(f"setWebhook error: {e}")
        return None


def make_inline_keyboard(buttons: list[list[dict]]) -> dict:
    """Create an inline keyboard markup.

    buttons: [[{'text': 'Label', 'callback_data': 'data'}], ...]
    """
    return {'inline_keyboard': buttons}
