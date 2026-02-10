#!/usr/bin/env python3
"""Run Gita Sarathi bot locally using Telegram long polling (no webhook needed)."""

import sys
import logging

# Configure logging FIRST before any imports
logging.basicConfig(
    stream=sys.stderr,
    format='%(asctime)s | %(levelname)s | %(message)s',
    level=logging.INFO,
    force=True,
)
logger = logging.getLogger('gitagpt.polling')

from dotenv import load_dotenv
load_dotenv()

import requests
from config import TELEGRAM_BOT_TOKEN, DB_PATH
from scripts.setup_db import setup_database

# Initialize DB
if not DB_PATH.exists():
    setup_database()

# Import handlers
from routes.telegram import _handle_command, _handle_text, _handle_voice, _handle_callback

BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


def get_updates(offset=None):
    params = {'timeout': 30}
    if offset is not None:
        params['offset'] = offset
    try:
        resp = requests.get(f"{BASE_URL}/getUpdates", params=params, timeout=35)
        data = resp.json()
        if data.get('ok'):
            return data.get('result', [])
    except requests.exceptions.Timeout:
        pass  # Normal for long polling
    except Exception as e:
        logger.error(f"getUpdates error: {e}")
    return []


def process_update(update):
    try:
        if 'callback_query' in update:
            _handle_callback(update['callback_query'])
        elif 'message' in update:
            msg = update['message']
            chat_id = msg['chat']['id']

            if 'voice' in msg:
                _handle_voice(chat_id, msg['voice'])
            elif 'text' in msg:
                text = msg['text'].strip()
                if text.startswith('/'):
                    _handle_command(chat_id, text)
                else:
                    _handle_text(chat_id, text)
    except Exception as e:
        logger.error(f"Error processing update: {e}", exc_info=True)


def main():
    logger.info("Starting Gita Sarathi bot...")

    # Delete any existing webhook first
    requests.post(f"{BASE_URL}/deleteWebhook", timeout=10)
    logger.info("Webhook deleted")

    # Verify bot
    resp = requests.get(f"{BASE_URL}/getMe", timeout=10).json()
    if resp.get('ok'):
        bot_name = resp['result']['username']
        logger.info(f"Bot connected: @{bot_name}")
        logger.info("Send a message to the bot on Telegram!")
    else:
        logger.error(f"Bot token invalid: {resp}")
        return

    # Flush any pending updates from previous runs
    flush_resp = requests.get(f"{BASE_URL}/getUpdates", params={'timeout': 0}, timeout=10).json()
    old = flush_resp.get('result', []) if flush_resp.get('ok') else []
    if old:
        offset = old[-1]['update_id'] + 1
        logger.info(f"Flushed {len(old)} old update(s)")
    else:
        offset = None

    while True:
        updates = get_updates(offset)
        for update in updates:
            offset = update['update_id'] + 1
            msg_text = update.get('message', {}).get('text', '[non-text]')
            logger.info(f"Received: {msg_text}")
            process_update(update)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped.")
