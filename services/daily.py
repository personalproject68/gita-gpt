"""Daily shloka push service — गीता यात्रा (sequential journey)."""

import json
import sqlite3
import logging
from config import DB_PATH
from models.shloka import (
    get_journey_shloka, get_chapter_info, is_chapter_complete,
    CHAPTER_NAMES, COMPLETE_SHLOKAS,
)
from services.ai_interpretation import get_ai_interpretation, get_daily_interpretation
from services.formatter import format_journey_shloka, format_chapter_milestone, format_journey_complete
from services.telegram_api import send_message, make_inline_keyboard

logger = logging.getLogger('gitagpt.daily')

TOTAL_SHLOKAS = len(COMPLETE_SHLOKAS)

# Auto-migrate: add journey_position column if missing
try:
    conn = sqlite3.connect(DB_PATH)
    conn.execute('ALTER TABLE subscribers ADD COLUMN journey_position INTEGER DEFAULT 0')
    conn.commit()
    conn.close()
    logger.info("Added journey_position column to subscribers")
except (sqlite3.OperationalError, Exception):
    pass  # Column already exists or table doesn't exist yet


def subscribe(user_id: str):
    """Auto-subscribe user to daily push."""
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            '''INSERT INTO subscribers (user_id, active) VALUES (?, 1)
               ON CONFLICT(user_id) DO UPDATE SET active = 1''',
            (user_id,),
        )
        conn.commit()
    finally:
        conn.close()


def unsubscribe(user_id: str):
    """Unsubscribe user from daily push."""
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute('UPDATE subscribers SET active = 0 WHERE user_id = ?', (user_id,))
        conn.commit()
    finally:
        conn.close()


def get_journey_position(user_id: str) -> int:
    """Get user's current journey position."""
    conn = sqlite3.connect(DB_PATH)
    try:
        row = conn.execute(
            'SELECT journey_position FROM subscribers WHERE user_id = ?', (user_id,)
        ).fetchone()
        return row[0] if row else 0
    finally:
        conn.close()


def advance_journey(user_id: str) -> int:
    """Advance user's journey by 1. Returns new position."""
    conn = sqlite3.connect(DB_PATH)
    try:
        row = conn.execute(
            'SELECT journey_position FROM subscribers WHERE user_id = ?', (user_id,)
        ).fetchone()
        current = row[0] if row else 0
        new_pos = min(current + 1, TOTAL_SHLOKAS - 1)
        conn.execute(
            '''INSERT INTO subscribers (user_id, active, journey_position) VALUES (?, 1, ?)
               ON CONFLICT(user_id) DO UPDATE SET journey_position = ?''',
            (user_id, new_pos, new_pos),
        )
        conn.commit()
        return new_pos
    finally:
        conn.close()


def get_active_subscribers() -> list[dict]:
    """Get all active subscribers with their journey position."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute('''
            SELECT user_id, journey_position
            FROM subscribers
            WHERE active = 1
        ''').fetchall()
        return [
            {'user_id': row['user_id'], 'journey_position': row['journey_position'] or 0}
            for row in rows
        ]
    finally:
        conn.close()


def _get_interpretation(shloka: dict) -> str:
    """Get interpretation: pre-fetched first, then live Gemini."""
    # Try pre-fetched
    interp = get_ai_interpretation("", [shloka])
    if interp:
        return interp
    # Fallback to live Gemini
    return get_daily_interpretation(shloka) or ""


def _make_next_button() -> dict:
    """Create 'अगला श्लोक →' inline button."""
    return make_inline_keyboard([[{
        'text': 'अगला श्लोक →',
        'callback_data': 'journey:next',
    }]])


def send_journey_shloka(user_id: str, position: int) -> tuple[str, dict | None]:
    """Format and return journey shloka message + reply_markup for a position."""
    if position >= TOTAL_SHLOKAS:
        return format_journey_complete(), None

    shloka = get_journey_shloka(position)
    if not shloka:
        return format_journey_complete(), None

    interpretation = _get_interpretation(shloka)
    chapter_info = get_chapter_info(position)
    chapter_name = chapter_info['name_hi'] if chapter_info else ''

    message = format_journey_shloka(shloka, interpretation, position, TOTAL_SHLOKAS, chapter_name)

    # Add chapter milestone if this is the last shloka of a chapter
    if is_chapter_complete(position) and chapter_info:
        ch = chapter_info['chapter']
        next_ch = ch + 1
        next_name = CHAPTER_NAMES.get(next_ch, '')
        message += '\n\n' + format_chapter_milestone(ch, chapter_name, position, TOTAL_SHLOKAS, next_ch, next_name)

    markup = _make_next_button() if position < TOTAL_SHLOKAS - 1 else None
    return message, markup


def send_daily_push() -> tuple[int, int]:
    """Send daily journey shloka to all subscribers. Returns (sent, failed)."""
    subscribers = get_active_subscribers()
    sent, failed = 0, 0

    for sub in subscribers:
        try:
            position = sub['journey_position']

            if position >= TOTAL_SHLOKAS:
                continue  # Journey complete, skip

            message, markup = send_journey_shloka(sub['user_id'], position)
            result = send_message(sub['user_id'], message, markup)

            if result and result.get('ok'):
                # Advance position after successful send
                advance_journey(sub['user_id'])
                sent += 1
            else:
                failed += 1
        except Exception as e:
            logger.error(f"Failed to send to {sub['user_id']}: {e}")
            failed += 1

    logger.info(f"Daily push: {sent} sent, {failed} failed")
    return sent, failed
