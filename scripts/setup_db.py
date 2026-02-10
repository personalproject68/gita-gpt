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

    # === OTP Auth tables ===
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS web_users (
            user_id TEXT PRIMARY KEY,
            phone TEXT UNIQUE NOT NULL,
            journey_position INTEGER DEFAULT 0,
            journey_streak INTEGER DEFAULT 0,
            journey_last_date TEXT,
            top_topics TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS web_sessions (
            token TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            FOREIGN KEY (user_id) REFERENCES web_users(user_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS otps (
            phone TEXT NOT NULL,
            request_id TEXT,
            attempts INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute(
        'CREATE INDEX IF NOT EXISTS idx_otps_phone_time ON otps(phone, created_at)'
    )

    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")


if __name__ == '__main__':
    setup_database()
