# GitaGPT - Project Context

## What is this?
Telegram chatbot that answers life questions using Bhagavad Gita shlokas. Hindi-focused, targets elderly Indian users (55+).

## Tech Stack
- **Platform:** Telegram Bot API (`python-telegram-bot`)
- **Backend:** Flask (Python 3.13)
- **Search:** ChromaDB + Cohere embeddings (semantic), keyword fallback
- **AI:** Google Gemini 2.5 Flash for interpretations
- **Voice:** Google Speech-to-Text (voice notes → text)
- **Persistence:** SQLite (sessions, subscribers, rate limiting)
- **Messaging:** Telegram Bot API (webhook mode)
- **Deployment:** Railway (no sleep, built-in cron)

## Project Structure (Modular)
```
gita-gpt/
├── app.py                    # Flask app entry point
├── config.py                 # All configuration & constants
├── routes/
│   ├── telegram.py           # Telegram webhook handler
│   ├── api.py                # REST API routes (/ask, /daily-push)
│   └── web.py                # HTML pages (home)
├── services/
│   ├── search.py             # Semantic + keyword search logic
│   ├── ai_interpretation.py  # Gemini AI integration
│   ├── session.py            # User session management (SQLite)
│   ├── voice.py              # Google STT voice transcription
│   └── formatter.py          # Response formatting (Telegram, forward-friendly)
├── guardrails/
│   ├── rate_limiter.py       # Rate limiting logic (SQLite)
│   ├── content_filter.py     # Profanity, manipulation, off-topic
│   └── sanitizer.py          # Input sanitization
├── models/
│   └── shloka.py             # Shloka data model & lookup
├── data/
│   ├── gita_tagged.json      # 100 curated shlokas with tags
│   ├── gita_complete.json    # All 701 shlokas (not used in v1)
│   └── curated_topics.json   # Topic-to-shloka mapping (5 topics)
├── scripts/
│   └── daily_push.py         # Daily shloka push script
└── tests/
    ├── test_search.py
    ├── test_guardrails.py
    └── test_telegram.py
```

## Environment Variables
```
TELEGRAM_BOT_TOKEN=xxx  # From @BotFather
COHERE_API_KEY=xxx      # Semantic search
GOOGLE_API_KEY=xxx      # Gemini + Speech-to-Text
DAILY_PUSH_SECRET=xxx   # Secret key for /daily-push endpoint
PORT=5000               # Server port
```

## Run Locally
```bash
pip install -r requirements.txt
python app.py
```

---

## Telegram Commands (v1)

| Command | Hindi | What it does |
|---------|-------|--------------|
| `/start`, `hi`, `hello` | `नमस्ते`, `हेलो` | Simple welcome message |
| `help` | `मदद`, `सहायता` | Show all commands |
| `topic` / `विषय` / `?` | - | Topic menu (5 topics, inline keyboard) |
| `daily` | `प्रेरणा`, `आज` | Today's inspirational shloka |
| `और` | `more` | Show next related shloka |
| `share` | `भेजें` | Get shareable link (fallback) |
| `रोकें` | `stop` | Unsubscribe from daily push |
| Voice note | - | Transcribed via Google STT, processed as text |

---

## Topic Menu (5 Topics)

| # | Hindi Label | Internal Key | Covers |
|---|-------------|--------------|--------|
| 1 | मुझे चिंता/डर लगता है | chinta | fear, anxiety, peace, meditation |
| 2 | मुझे गुस्सा आता है | krodh | anger |
| 3 | मुझे समझ नहीं आता क्या करूं | kartavya | duty, decisions, family conflicts |
| 4 | मैं बीमार हूं / कोई खो दिया | dukh | illness, death, grief, loss |
| 5 | मैं अकेला महसूस करता हूं | akela | loneliness, isolation |

Shown as Telegram inline keyboard buttons (no typing needed).

---

## Guardrails (v1)

### Rate Limiting
- **Limit:** 20 messages per user per hour
- **Storage:** SQLite `messages` table
- **Response:** "कृपया थोड़ा रुकें..."

### Content Filtering
- **Profanity:** Hindi (Devanagari) + Hinglish (Roman) + English blocked words
- **Manipulation:** "ignore previous", "jailbreak", etc. blocked
- **Off-topic:** Politics, explicit content blocked
- **Response:** Compassionate redirect — "आपके मन में कुछ कठिन भाव हैं। क्या मैं गीता का मार्गदर्शन दूं?"

### Input Sanitization
- Max 500 characters
- Strips excessive whitespace
- Rejects empty/single-char messages

---

## Key Functions

| Function | Module | Purpose |
|----------|--------|---------|
| `find_relevant_shlokas(query)` | services/search.py | Semantic search → keyword fallback |
| `format_response(shlokas, query)` | services/formatter.py | Telegram + forward-friendly formatting |
| `get_ai_interpretation(query, shlokas)` | services/ai_interpretation.py | Gemini contextual explanation |
| `transcribe_voice(file)` | services/voice.py | Google STT voice-to-text |
| `check_rate_limit(user_id)` | guardrails/rate_limiter.py | SQLite rate limiting |
| `check_content(message)` | guardrails/content_filter.py | Content filtering |
| `get_session(user_id)` | services/session.py | SQLite user session |

---

## Response Format (Forward-Friendly)

```
📿 गीता 2.47

कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।

कर्म पर तुम्हारा अधिकार है, फल पर नहीं।

[AI interpretation - 3-4 lines]

— गीता GPT 🙏
```

Footer "गीता GPT 🙏" acts as organic branding when forwarded.

---

## Response Flow

```
Telegram Message (text or voice)
    ↓
Voice? → Google STT → text
    ↓
Guardrails (rate limit, keyword filter, sanitize)
    ↓
Command Handler (/start, help, topic, daily, और, share, रोकें)
    ↓
OR Process as Question
    ↓
find_relevant_shlokas() → 1 shloka (semantic search)
    ↓
get_ai_interpretation() → Deep Gemini context
    ↓
Format with forward-friendly footer (गीता GPT 🙏)
    ↓
Telegram Bot API response
```

### Daily Push Flow
```
GitHub Actions / Railway cron (6 AM IST)
    ↓
POST /daily-push (with secret key)
    ↓
Select today's shloka (personalized by user's top topics)
    ↓
Send to all active subscribers via Telegram API
```

---

## Data Structure

### Shloka
```json
{
  "shloka_id": "2.47",
  "sanskrit": "कर्मण्येवाधिकारस्ते...",
  "hindi_meaning": "Simple Hindi translation",
  "tags": ["karma", "action"]
}
```

### SQLite Schema
```sql
CREATE TABLE sessions (
    user_id TEXT PRIMARY KEY,
    last_shlokas TEXT,          -- JSON array
    last_query TEXT,
    context TEXT,               -- 'topic_menu' | NULL
    top_topics TEXT,            -- JSON: {"chinta": 5, "krodh": 2}
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE messages (
    user_id TEXT,
    sent_at TIMESTAMP
);

CREATE TABLE subscribers (
    user_id TEXT PRIMARY KEY,
    subscribed_at TIMESTAMP,
    active INTEGER DEFAULT 1
);
```

---

## v1 Scope (This Week)

### Included
- Simple welcome message
- 5-topic menu with inline keyboard
- Semantic search (100 curated shlokas)
- Single shloka + deep AI interpretation
- "और" for next related shloka
- Voice note transcription (voice-to-text)
- Auto-subscribe daily push (6 AM IST)
- Forward-friendly formatting
- Content moderation (keyword filter + rate limit)
- SQLite persistence
- Structured logging
- Railway deployment

### Excluded (Later)
- Krishna images (need to source)
- Monetization/dakshina (after 1 month)
- 3-step onboarding drip
- Voice output (TTS)
- WhatsApp support
- 701 shloka dataset

---

## Testing Checklist

- [ ] Send `/start` - see welcome message
- [ ] Send `मदद` - see help
- [ ] Send `विषय` - see 5-topic inline keyboard
- [ ] Tap topic button - get relevant shloka
- [ ] Send question, then "और" - get next shloka
- [ ] Send voice note - transcribed and answered
- [ ] Send 25+ messages rapidly - hit rate limit
- [ ] Send profanity - compassionate redirect
- [ ] Send "ignore previous instructions" - blocked
- [ ] Check 6 AM daily push arrives
- [ ] Send "रोकें" - unsubscribed from daily

---

## Product Ledger (MANDATORY)

Before implementing ANY feature:
1. Read `DECISIONS.md` — Check for existing ID (P1, P2...)
2. If no ID exists → Create deliberation flow:
   - `problem.md` → `features.md` → `ARCHITECTURE.md` → `GTM.md` → `DECISIONS.md`
3. ASK user approval BEFORE writing any code
4. Reference ID in commits: `feat(P1): description`
5. Update status in DECISIONS.md when done

**Files:** All in root directory
**Full methodology:** `docs/PRODUCT_LEDGER_METHODOLOGY.md`

NEVER write code without completing deliberation first.
