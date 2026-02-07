"""Daily shloka push service."""

import json
import sqlite3
import logging
from config import DB_PATH
from models.shloka import get_daily_shloka
from services.ai_interpretation import get_daily_interpretation
from services.formatter import format_daily_shloka
from services.telegram_api import send_message

logger = logging.getLogger('gitagpt.daily')


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


def get_active_subscribers() -> list[dict]:
    """Get all active subscribers with their top topics."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute('''
            SELECT s.user_id, sess.top_topics
            FROM subscribers s
            LEFT JOIN sessions sess ON s.user_id = sess.user_id
            WHERE s.active = 1
        ''').fetchall()
        result = []
        for row in rows:
            top_topics = json.loads(row['top_topics'] or '{}') if row['top_topics'] else {}
            result.append({'user_id': row['user_id'], 'top_topics': top_topics})
        return result
    finally:
        conn.close()


def _get_top_topic(top_topics: dict) -> str | None:
    """Get user's most-asked topic."""
    if not top_topics:
        return None
    return max(top_topics, key=top_topics.get)


def send_daily_push() -> tuple[int, int]:
    """Send daily shloka to all subscribers. Returns (sent, failed)."""
    subscribers = get_active_subscribers()
    sent, failed = 0, 0

    for sub in subscribers:
        try:
            top_topic = _get_top_topic(sub['top_topics'])
            shloka = get_daily_shloka(topic=top_topic)
            
            # Use AI interpretation for daily push
            interpretation = get_daily_interpretation(shloka)
            message = format_daily_shloka(shloka, interpretation)

            result = send_message(sub['user_id'], message)
            if result and result.get('ok'):
                sent += 1
            else:
                failed += 1
        except Exception as e:
            logger.error(f"Failed to send to {sub['user_id']}: {e}")
            failed += 1

    logger.info(f"Daily push: {sent} sent, {failed} failed")
    return sent, failed
