"""SQLite-backed user session management."""

import json
import sqlite3
import logging
from datetime import datetime
from config import DB_PATH

logger = logging.getLogger('gitagpt.session')


def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_session(user_id: str) -> dict:
    """Get or create user session."""
    conn = _get_conn()
    try:
        row = conn.execute('SELECT * FROM sessions WHERE user_id = ?', (user_id,)).fetchone()
        if row:
            return {
                'user_id': row['user_id'],
                'last_shlokas': json.loads(row['last_shlokas'] or '[]'),
                'last_query': row['last_query'] or '',
                'context': row['context'],
                'top_topics': json.loads(row['top_topics'] or '{}'),
            }
        # Create new session
        conn.execute(
            'INSERT INTO sessions (user_id, last_shlokas, last_query, context, top_topics) VALUES (?, ?, ?, ?, ?)',
            (user_id, '[]', '', None, '{}'),
        )
        conn.commit()
        return {
            'user_id': user_id,
            'last_shlokas': [],
            'last_query': '',
            'context': None,
            'top_topics': {},
        }
    finally:
        conn.close()


def save_session(user_id: str, query: str, shlokas: list[dict], context: str = None):
    """Save query results to session."""
    shloka_data = json.dumps([{
        'shloka_id': s['shloka_id'],
        'sanskrit': s['sanskrit'],
        'hindi_meaning': s['hindi_meaning'],
    } for s in shlokas], ensure_ascii=False)

    conn = _get_conn()
    try:
        conn.execute(
            '''INSERT INTO sessions (user_id, last_shlokas, last_query, context, updated_at)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(user_id) DO UPDATE SET
               last_shlokas = excluded.last_shlokas,
               last_query = excluded.last_query,
               context = excluded.context,
               updated_at = excluded.updated_at''',
            (user_id, shloka_data, query, context, datetime.now()),
        )
        conn.commit()
    finally:
        conn.close()


def update_context(user_id: str, context: str | None):
    """Update session context (e.g., 'topic_menu')."""
    conn = _get_conn()
    try:
        conn.execute(
            'UPDATE sessions SET context = ?, updated_at = ? WHERE user_id = ?',
            (context, datetime.now(), user_id),
        )
        conn.commit()
    finally:
        conn.close()


def update_top_topics(user_id: str, topic: str):
    """Increment topic counter for personalized daily push."""
    session = get_session(user_id)
    topics = session['top_topics']
    topics[topic] = topics.get(topic, 0) + 1

    conn = _get_conn()
    try:
        conn.execute(
            'UPDATE sessions SET top_topics = ?, updated_at = ? WHERE user_id = ?',
            (json.dumps(topics, ensure_ascii=False), datetime.now(), user_id),
        )
        conn.commit()
    finally:
        conn.close()
