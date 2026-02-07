"""SQLite-backed rate limiting."""

import sqlite3
import logging
from datetime import datetime, timedelta
from config import DB_PATH, RATE_LIMIT, RATE_WINDOW

logger = logging.getLogger('gitagpt.rate_limiter')


def check_rate_limit(user_id: str) -> bool:
    """Check if user is within rate limit. Returns True if OK, False if limited."""
    conn = sqlite3.connect(DB_PATH)
    try:
        cutoff = datetime.now() - timedelta(seconds=RATE_WINDOW)

        # Count recent messages
        row = conn.execute(
            'SELECT COUNT(*) FROM messages WHERE user_id = ? AND sent_at > ?',
            (user_id, cutoff),
        ).fetchone()

        count = row[0] if row else 0

        if count >= RATE_LIMIT:
            logger.warning(f"Rate limited: {user_id} ({count} msgs)")
            return False

        # Record this message
        conn.execute(
            'INSERT INTO messages (user_id, sent_at) VALUES (?, ?)',
            (user_id, datetime.now()),
        )
        conn.commit()
        return True
    finally:
        conn.close()


def cleanup_old_messages():
    """Remove messages older than the rate window (housekeeping)."""
    conn = sqlite3.connect(DB_PATH)
    try:
        cutoff = datetime.now() - timedelta(seconds=RATE_WINDOW * 2)
        conn.execute('DELETE FROM messages WHERE sent_at < ?', (cutoff,))
        conn.commit()
    finally:
        conn.close()
