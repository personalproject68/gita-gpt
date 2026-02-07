# GitaGPT - Architecture (Telegram v1)

## Overview

Telegram bot built with modular Flask backend. Clean rewrite from WhatsApp MVP — reuses only core logic (search, AI interpretation, data).

---

## Platform: Telegram Bot API

| Factor | Detail |
|--------|--------|
| Library | `python-telegram-bot` |
| Mode | Webhook (Flask receives updates) |
| Rich UI | Inline keyboard buttons for topic menu |
| Voice | Native voice message support |
| Cost | Free (Telegram Bot API has no per-message cost) |
| Setup | @BotFather → get token → set webhook |

**WhatsApp (Phase 2):** After PMF + revenue, migrate to Meta Business API directly (~₹18K/mo). Skip Twilio.

---

## Project Structure

```
gita-gpt/
├── app.py                    # Flask entry point (~50 lines)
├── config.py                 # All configuration & constants
├── routes/
│   ├── __init__.py
│   ├── telegram.py           # Telegram webhook handler
│   ├── api.py                # REST API (/ask, /daily-push)
│   └── web.py                # HTML pages (home)
├── services/
│   ├── __init__.py
│   ├── search.py             # ChromaDB semantic + keyword fallback
│   ├── ai_interpretation.py  # Gemini AI integration
│   ├── session.py            # SQLite session management
│   ├── voice.py              # Google STT voice transcription
│   ├── daily.py              # Daily push logic
│   └── formatter.py          # Response formatting (forward-friendly)
├── guardrails/
│   ├── __init__.py
│   ├── rate_limiter.py       # SQLite rate limiting
│   ├── content_filter.py     # Profanity, manipulation, off-topic
│   └── sanitizer.py          # Input sanitization
├── models/
│   ├── __init__.py
│   └── shloka.py             # Shloka data model & lookup
├── data/
│   ├── gita_tagged.json      # 100 curated shlokas
│   ├── gita_complete.json    # 701 shlokas (not used in v1)
│   └── curated_topics.json   # 5 topic-to-shloka mapping
├── scripts/
│   └── setup_db.py           # SQLite schema initialization
└── tests/
    ├── test_search.py
    ├── test_guardrails.py
    └── test_telegram.py
```

---

## Database: SQLite

Replace in-memory `USER_SESSIONS` dict with SQLite. Survives restarts.

### Schema

```sql
-- User sessions
CREATE TABLE sessions (
    user_id TEXT PRIMARY KEY,
    last_shlokas TEXT,          -- JSON array of shloka objects
    last_query TEXT,
    context TEXT,               -- 'topic_menu' | NULL
    top_topics TEXT,            -- JSON: {"chinta": 5, "krodh": 2}
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Rate limiting
CREATE TABLE messages (
    user_id TEXT,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_messages_user_time ON messages(user_id, sent_at);

-- Daily push subscribers
CREATE TABLE subscribers (
    user_id TEXT PRIMARY KEY,
    subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    active INTEGER DEFAULT 1
);
```

**Why SQLite:** Zero config, single file, ships with Python, handles 10K+ concurrent reads. Overkill threshold: ~100K users.

---

## Search: ChromaDB + Cohere

Kept from MVP. Already working, battle-tested.

- **Embeddings:** Cohere `embed-multilingual-v3.0`
- **Vector DB:** ChromaDB (persistent storage)
- **Dataset:** 100 curated shlokas (`gita_tagged.json`)
- **Fallback:** Keyword search on tags when semantic returns low confidence

---

## AI: Google Gemini 2.5 Flash

- Contextual interpretation of shlokas
- 3-4 line explanation connecting shloka to user's question
- Hindi output
- Prompt template: empathy → teaching → practical takeaway

---

## Voice: Google Speech-to-Text

| Config | Value |
|--------|-------|
| API | Google Cloud Speech-to-Text v1 |
| Language | `hi-IN` (Hindi) |
| Audio format | OGG (Telegram native) → converted if needed |
| Max duration | 60 seconds |
| Cost | ~$0.006 per 15 seconds |
| Auth | Same `GOOGLE_API_KEY` as Gemini |

### Flow:
1. Telegram sends voice message → bot gets `file_id`
2. Download .ogg via Telegram `getFile` API
3. Send to Google STT → get Hindi transcription
4. Process transcription as normal text query
5. On failure: "मुझे आपकी बात समझ नहीं आई। कृपया टाइप करके भेजें।"

---

## Deployment: Railway

| Factor | Railway |
|--------|---------|
| Cost | Free tier → $5/mo |
| Sleep | No sleep on free tier |
| Cron | Built-in cron support |
| Deploy | `railway up` or Git push |
| SQLite | Works (persistent volume) |

### Daily Push Cron
- Railway cron job at 6:00 AM IST (00:30 UTC)
- Hits `POST /daily-push` with secret key
- Alternative: GitHub Actions cron as backup

---

## Logging

Structured logging for debugging real user issues.

```python
import logging
logging.basicConfig(
    filename='gitagpt.log',
    format='%(asctime)s | %(levelname)s | %(message)s'
)
```

**What to log:**
- Every search query + number of results found
- Gemini API response time
- Voice transcription success/failure
- Errors (API failures, malformed input)
- Rate limit triggers
- Daily push success/failure count

---

## Module Responsibilities

### config.py
- Environment variables (tokens, API keys)
- Rate limit constants
- Blocked word lists
- Topic menu definitions
- Logging config

### routes/telegram.py
- Telegram webhook endpoint
- Message routing (text, voice, callback query)
- Command dispatch (/start, help, topic, daily, और, share, रोकें)

### routes/api.py
- `POST /daily-push` — Daily shloka to all subscribers
- `GET /ask?q=...` — REST API for web interface
- `GET /health` — Health check

### routes/web.py
- `GET /` — Home page

### services/search.py
- `find_relevant_shlokas(query)` — Main search (semantic → keyword)
- ChromaDB collection management
- Tag-based topic search

### services/ai_interpretation.py
- `get_ai_interpretation(query, shlokas)` — Gemini contextual explanation

### services/session.py
- `get_session(user_id)` — Read from SQLite
- `save_session(user_id, data)` — Write to SQLite
- `update_top_topics(user_id, topic)` — Track engagement

### services/voice.py
- `transcribe_voice(file_path)` — Google STT
- Download Telegram voice file
- OGG handling

### services/daily.py
- `send_daily_push()` — Send to all active subscribers
- `subscribe(user_id)` / `unsubscribe(user_id)`
- Shloka selection (personalized by top topics)

### services/formatter.py
- `format_shloka(shloka, interpretation)` — Forward-friendly format
- `format_welcome()` — Welcome message
- `format_help()` — Help message
- `format_topic_menu()` — Inline keyboard builder

### guardrails/rate_limiter.py
- `check_rate_limit(user_id)` — 20 msgs/hr, SQLite-backed

### guardrails/content_filter.py
- `check_content(message)` — Keyword filter (Hindi + Hinglish + English)

### guardrails/sanitizer.py
- `sanitize_input(message)` — Length, whitespace, empty check

### models/shloka.py
- Load `gita_tagged.json`
- Load `curated_topics.json`
- `get_daily_shloka(topic=None)` — Random/personalized selection

---

## Entry Point: app.py

```python
from flask import Flask
from config import PORT
from routes import telegram, api, web

app = Flask(__name__)

app.register_blueprint(telegram.bp)
app.register_blueprint(api.bp)
app.register_blueprint(web.bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True)
```

---

## Cost Per Message (Telegram)

| Component | Cost |
|-----------|------|
| Telegram Bot API | Free |
| Cohere embedding | ₹0.008 |
| Gemini AI | ₹0.008 |
| Google STT (voice only) | ₹0.05 |
| **Text message total** | **₹0.016** |
| **Voice message total** | **₹0.066** |

### Monthly (1000 users, 3 msgs/day)
- Server (Railway): ₹0-400
- AI APIs: ₹1,440
- Google STT (assuming 30% voice): ₹1,800
- **Total: ~₹3,600/mo**

---

## Phase 2: Post-PMF Additions

Only after validating on Telegram with real users:

1. **Krishna images** — Source and add to daily push
2. **Onboarding drip** — 3-step progressive feature reveal
3. **Monetization** — Dakshina/seva commands, UPI QR, Razorpay
4. **Voice output** — TTS for audio responses
5. **WhatsApp** — Meta Business API integration
6. **701 shlokas** — Expand dataset based on query gaps
7. **Empathy arc** — AI interpretation with emotion acknowledgment first
