"""Lightweight metrics: event logging + daily stats."""

import sqlite3
import logging
from datetime import datetime, timedelta
from config import DB_PATH

logger = logging.getLogger('gitagpt.metrics')


def log_event(event_type: str, user_id: str = None, data: str = None):
    """Append an event to the events table."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            'INSERT INTO events (event_type, user_id, data, created_at) VALUES (?, ?, ?, ?)',
            (event_type, user_id, data, datetime.now()),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to log event: {e}")


def get_daily_stats() -> dict:
    """Get yesterday's key metrics."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    now = datetime.now()
    yesterday_start = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_end = yesterday_start + timedelta(days=1)

    try:
        # DAU yesterday
        dau = conn.execute(
            'SELECT COUNT(DISTINCT user_id) FROM messages WHERE sent_at BETWEEN ? AND ?',
            (yesterday_start, yesterday_end),
        ).fetchone()[0]

        # New users yesterday
        new_users = conn.execute(
            'SELECT COUNT(*) FROM sessions WHERE created_at BETWEEN ? AND ?',
            (yesterday_start, yesterday_end),
        ).fetchone()[0]

        # Total messages yesterday
        total_messages = conn.execute(
            'SELECT COUNT(*) FROM messages WHERE sent_at BETWEEN ? AND ?',
            (yesterday_start, yesterday_end),
        ).fetchone()[0]

        # Active subscribers (all-time)
        active_subs = conn.execute(
            'SELECT COUNT(*) FROM subscribers WHERE active = 1',
        ).fetchone()[0]

        # API failures yesterday
        api_failures = conn.execute(
            'SELECT COUNT(*) FROM events WHERE event_type = ? AND created_at BETWEEN ? AND ?',
            ('api_error', yesterday_start, yesterday_end),
        ).fetchone()[0]

        return {
            'date': yesterday_start.strftime('%d %b %Y'),
            'dau': dau,
            'new_users': new_users,
            'total_messages': total_messages,
            'active_subscribers': active_subs,
            'api_failures': api_failures,
        }
    except Exception as e:
        logger.error(f"Stats query error: {e}")
        return None
    finally:
        conn.close()
