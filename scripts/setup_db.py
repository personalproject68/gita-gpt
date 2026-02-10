"""Initialize Gita Sarathi SQLite database."""

import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import DB_PATH


def setup_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            user_id TEXT PRIMARY KEY,
            last_shlokas TEXT,
            last_query TEXT,
            context TEXT,
            top_topics TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            user_id TEXT,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute(
        'CREATE INDEX IF NOT EXISTS idx_messages_user_time ON messages(user_id, sent_at)'
    )

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            event_type TEXT,
            user_id TEXT,
            data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute(
        'CREATE INDEX IF NOT EXISTS idx_events_type_time ON events(event_type, created_at)'
    )

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscribers (
            user_id TEXT PRIMARY KEY,
            subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            active INTEGER DEFAULT 1,
            journey_position INTEGER DEFAULT 0
        )
    ''')

    # Migration: add journey_position if table already exists without it
    try:
        cursor.execute('ALTER TABLE subscribers ADD COLUMN journey_position INTEGER DEFAULT 0')
    except sqlite3.OperationalError:
        pass  # Column already exists

    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")


if __name__ == '__main__':
    setup_database()
