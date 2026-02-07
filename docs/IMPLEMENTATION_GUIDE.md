# GitaGPT Telegram Bot - Complete Implementation Guide

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Current State Analysis](#current-state-analysis)
3. [Architecture Design](#architecture-design)
4. [Phase-by-Phase Implementation](#phase-by-phase-implementation)
5. [Code Templates](#code-templates)
6. [Testing Guide](#testing-guide)
7. [Deployment Guide](#deployment-guide)

---

## 1. Project Overview

### Objective
Migrate GitaGPT from WhatsApp (monolithic 1054-line app.py) to Telegram with a clean, modular architecture.

### Why This Migration?
- **Cost**: Telegram is free vs WhatsApp (₹41K/mo via Twilio)
- **Features**: Better support for inline keyboards, voice messages, no sleep
- **Architecture**: Modular design vs monolithic code
- **Persistence**: SQLite vs in-memory (survives restarts)

### Key Features (v1)
1. ✅ Semantic search (ChromaDB + Cohere) - 99 curated shlokas
2. ✅ AI interpretation (Gemini 2.5 Flash) - contextual Hindi explanations
3. ✅ Topic menu - 5 topics with inline keyboard buttons
4. ✅ Voice-to-text - Google Speech-to-Text for Hindi
5. ✅ Daily shloka push - Auto-subscribe, personalized by engagement
6. ✅ Guardrails - Rate limiting, content filtering, sanitization
7. ✅ Forward-friendly formatting - "गीता GPT 🙏" footer

---

## 2. Current State Analysis

### ✅ Assets Ready

**API Keys (in .env)** — See `.env.example` for required variables. Never commit real keys.

**Data Files**
- ✅ `data/gita_tagged.json` - 701 complete shlokas with tags
- ✅ `data/gita_mvp.json` - 99 curated shlokas for MVP
- ⚠️ `data/curated_topics.json` - Has 15 topics, needs consolidation to 5
- ✅ `data/chromadb_mvp/` - Pre-generated embeddings (reuse as-is)

**WhatsApp MVP Code (app.py - 1054 lines)**

Key components to extract:
```
Lines 195-268  → SemanticSearch class
Lines 271-372  → find_relevant_shlokas()
Lines 481-514  → get_ai_interpretation()
Lines 75-91    → check_rate_limit()
Lines 94-116   → check_content()
Lines 119-125  → sanitize_input()
Lines 26-44    → Guardrail constants
Lines 167-191  → Data loading
```

### ⚠️ Gaps to Fill

1. **No modular structure** - Need to create routes/, services/, guardrails/, models/ directories
2. **curated_topics.json** - Needs update from 15 topics → 5 topics
3. **No SQLite database** - Need to create schema and migration from in-memory
4. **No Telegram integration** - python-telegram-bot not implemented
5. **No deployment config** - Missing Procfile, railway.json

---

## 3. Architecture Design

### Target Structure
```
gita-gpt/
├── app.py                    # Flask entry point (~20 lines)
├── config.py                 # All configuration & constants
├── gitagpt.db                # SQLite database (generated)
│
├── routes/
│   ├── __init__.py
│   ├── telegram.py           # Telegram webhook handler
│   ├── api.py                # REST API (/ask, /daily-push)
│   └── web.py                # HTML home page
│
├── services/
│   ├── __init__.py
│   ├── search.py             # Semantic + keyword search
│   ├── ai_interpretation.py  # Gemini AI integration
│   ├── session.py            # SQLite session management
│   ├── voice.py              # Google STT transcription
│   ├── daily.py              # Daily push logic
│   └── formatter.py          # Telegram response formatting
│
├── guardrails/
│   ├── __init__.py
│   ├── rate_limiter.py       # Rate limiting (SQLite)
│   ├── content_filter.py     # Profanity/manipulation filter
│   └── sanitizer.py          # Input sanitization
│
├── models/
│   ├── __init__.py
│   └── shloka.py             # Shloka data model & lookup
│
├── scripts/
│   └── setup_db.py           # Database initialization
│
└── data/                     # (existing, minimal changes)
    ├── gita_tagged.json
    ├── gita_mvp.json
    ├── curated_topics.json   # UPDATE THIS
    └── chromadb_mvp/
```

### SQLite Schema
```sql
-- User sessions
CREATE TABLE sessions (
    user_id TEXT PRIMARY KEY,
    last_shlokas TEXT,          -- JSON: [shloka objects]
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

---

## 4. Phase-by-Phase Implementation

### PHASE 1: Data Preparation (2 hours)

#### 1.1 Update curated_topics.json

**Current:** 15 topics (bhay_dar, krodh_gussa, dukh_pareshani, man_shanti, karma_kartavya, mrityu_loss, parivar_rishte, sanshay_confusion, dhyan_focus, bhakti_shraddha, ahankar_ego, tyag_detachment, himmat_courage, sukh_happiness, gyan_wisdom)

**Target:** 5 topics for v1

**Mapping Strategy:**

| New ID | Hindi Label | Merge From | Best Shlokas |
|--------|-------------|------------|--------------|
| `chinta` | मुझे चिंता/डर लगता है | bhay_dar + man_shanti + dhyan_focus | 2.14, 2.15, 2.56, 4.10, 6.35, 2.64, 2.65, 2.70, 6.7, 6.10, 6.25 (~11 shlokas) |
| `krodh` | मुझे गुस्सा आता है | krodh_gussa (keep) | 2.62, 2.63, 3.37, 5.26, 16.21 (5 shlokas) |
| `kartavya` | मुझे समझ नहीं आता क्या करूं | karma_kartavya + sanshay_confusion + parivar_rishte | 2.47, 2.48, 3.8, 3.19, 4.18, 2.7, 4.35, 4.40, 1.28, 3.21 (~10 shlokas) |
| `dukh` | मैं बीमार हूं / कोई खो दिया | mrityu_loss + dukh_pareshani | 2.11, 2.13, 2.20, 2.22, 2.27, 2.14, 2.15, 5.20, 6.20 (~9 shlokas) |
| `akela` | मैं अकेला महसूस करता हूं | NEW (gyan_wisdom + bhakti_shraddha + sukh_happiness) | 9.22, 9.26, 9.29, 12.13, 12.14, 5.21, 6.27 (~7 shlokas) |

**Updated curated_topics.json:**
```json
{
  "chinta": {
    "name_hi": "मुझे चिंता/डर लगता है",
    "name_en": "Fear, Anxiety, Peace",
    "best_shlokas": ["2.14", "2.15", "2.56", "4.10", "6.35", "2.64", "2.65", "2.70", "6.7", "6.10", "6.25"],
    "keywords": ["डर", "भय", "चिंता", "घबराहट", "शांति", "मन", "ध्यान", "fear", "anxiety", "worried", "peace", "calm", "meditation"]
  },
  "krodh": {
    "name_hi": "मुझे गुस्सा आता है",
    "name_en": "Anger",
    "best_shlokas": ["2.62", "2.63", "3.37", "5.26", "16.21"],
    "keywords": ["गुस्सा", "क्रोध", "चिड़चिड़ा", "anger", "angry", "irritated", "rage", "frustration"]
  },
  "kartavya": {
    "name_hi": "मुझे समझ नहीं आता क्या करूं",
    "name_en": "Duty, Decisions, Confusion",
    "best_shlokas": ["2.47", "2.48", "3.8", "3.19", "4.18", "2.7", "4.35", "4.40", "1.28", "3.21"],
    "keywords": ["कर्म", "कर्तव्य", "संशय", "भ्रम", "परिवार", "निर्णय", "duty", "karma", "decision", "confused", "what to do", "family", "responsibility"]
  },
  "dukh": {
    "name_hi": "मैं बीमार हूं / कोई खो दिया",
    "name_en": "Illness, Death, Grief, Loss",
    "best_shlokas": ["2.11", "2.13", "2.20", "2.22", "2.27", "2.14", "2.15", "5.20", "6.20"],
    "keywords": ["मृत्यु", "मौत", "दुख", "तकलीफ", "बीमारी", "खो दिया", "death", "loss", "grief", "sick", "illness", "suffering", "pain"]
  },
  "akela": {
    "name_hi": "मैं अकेला महसूस करता हूं",
    "name_en": "Loneliness, Isolation",
    "best_shlokas": ["9.22", "9.26", "9.29", "12.13", "12.14", "5.21", "6.27"],
    "keywords": ["अकेला", "अकेलापन", "एकाकी", "तन्हा", "loneliness", "alone", "lonely", "isolated", "isolation"]
  }
}
```

**Action:** Update `/Users/ashishgupta/Desktop/ \/gita-gpt/data/curated_topics.json` with above content

---

#### 1.2 Create Database Setup Script

**File:** `scripts/setup_db.py`

```python
#!/usr/bin/env python3
"""
Database setup script for GitaGPT Telegram bot.
Creates SQLite database with required tables.
"""

import sqlite3
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent.parent / 'gitagpt.db'

def setup_database():
    """Initialize SQLite database with schema."""
    print(f"Setting up database at: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Sessions table - stores user conversation context
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            user_id TEXT PRIMARY KEY,
            last_shlokas TEXT,          -- JSON array of shloka objects
            last_query TEXT,            -- Last question asked
            context TEXT,               -- Current context: 'topic_menu' | NULL
            top_topics TEXT,            -- JSON object: {"chinta": 5, "krodh": 2}
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✓ Created sessions table")

    # Messages table - for rate limiting
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            user_id TEXT,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_messages_user_time
        ON messages(user_id, sent_at)
    ''')
    print("✓ Created messages table with index")

    # Subscribers table - for daily push
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscribers (
            user_id TEXT PRIMARY KEY,
            subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            active INTEGER DEFAULT 1
        )
    ''')
    print("✓ Created subscribers table")

    conn.commit()
    conn.close()

    print(f"\n✅ Database initialized successfully!")
    print(f"Location: {DB_PATH}")

if __name__ == '__main__':
    setup_database()
```

**Run:**
```bash
python scripts/setup_db.py
```

---

### PHASE 2: Core Infrastructure (1 hour)

#### 2.1 config.py - Centralized Configuration

**File:** `config.py`

```python
"""
GitaGPT Configuration
All environment variables, constants, and configuration in one place.
"""

import os
import logging
from pathlib import Path

# ============ Environment Variables ============

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
COHERE_API_KEY = os.environ.get('COHERE_API_KEY')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
DAILY_PUSH_SECRET = os.environ.get('DAILY_PUSH_SECRET')
PORT = int(os.environ.get('PORT', 5000))

# ============ Paths ============

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'
DB_PATH = BASE_DIR / 'gitagpt.db'
CHROMADB_PATH = DATA_DIR / 'chromadb_mvp'

# ============ Rate Limiting ============

RATE_LIMIT = 20         # Messages per user
RATE_WINDOW = 3600      # 1 hour in seconds

# ============ Guardrails ============

# Blocked words (Hindi Devanagari + Hinglish + English)
BLOCKED_WORDS = [
    # Hindi profanity (Devanagari)
    'भड़वा', 'रंडी', 'चूतिया', 'मादरचोद', 'बहनचोद',
    'गांड', 'लौड़ा', 'भोसड़ी',
    # Hinglish variants
    'bhadvaa', 'randi', 'chutiya', 'madarc', 'bhencho',
    'gaand', 'lauda', 'bhosdi',
    # English profanity
    'fuck', 'shit', 'ass', 'bitch', 'bastard', 'dick', 'pussy',
]

# Manipulation/jailbreak patterns
MANIPULATION_PATTERNS = [
    'ignore previous', 'forget instructions', 'you are now', 'act as',
    'pretend to be', 'bypass', 'ignore all', 'disregard', 'new persona',
    'jailbreak', 'dan mode', 'developer mode', 'ignore safety',
]

# Off-topic keywords
OFFTOPIC_KEYWORDS = [
    'modi', 'rahul', 'bjp', 'congress', 'election', 'vote', 'pakistan',
    'muslim', 'hindu', 'christian', 'sex', 'porn', 'nude', 'xxx',
]

# ============ Telegram Topic Menu ============

TOPIC_MENU = {
    'chinta': 'मुझे चिंता/डर लगता है',
    'krodh': 'मुझे गुस्सा आता है',
    'kartavya': 'मुझे समझ नहीं आता क्या करूं',
    'dukh': 'मैं बीमार हूं / कोई खो दिया',
    'akela': 'मैं अकेला महसूस करता हूं'
}

# ============ Logging ============

logging.basicConfig(
    filename='gitagpt.log',
    format='%(asctime)s | %(levelname)s | %(message)s',
    level=logging.INFO
)

# ============ Search Configuration ============

COHERE_MODEL = 'embed-multilingual-v3.0'
CHROMADB_COLLECTION = 'gita_mvp'
SEARCH_RESULTS_DEFAULT = 1  # Return 1 shloka by default for v1

# ============ AI Configuration ============

GEMINI_MODEL = 'gemini-2.5-flash'
AI_INTERPRETATION_MAX_LENGTH = 300  # chars per shloka meaning in prompt

# ============ Input Limits ============

MAX_INPUT_LENGTH = 500  # characters
MIN_INPUT_LENGTH = 2    # characters

# ============ Daily Shloka ============

FAMOUS_SHLOKA_IDS = [
    '2.47', '2.14', '2.22', '2.27', '3.35',
    '4.7', '6.5', '9.22', '18.66'
]
```

---

#### 2.2 models/shloka.py - Data Loading

**File:** `models/shloka.py`

```python
"""
Shloka data model and loading.
Loads gita_mvp.json and curated_topics.json.
"""

import json
import random
from config import DATA_DIR, FAMOUS_SHLOKA_IDS

# ============ Load Data ============

def load_shlokas():
    """Load all shlokas from gita_mvp.json."""
    with open(DATA_DIR / 'gita_mvp.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_curated_topics():
    """Load curated topic mappings."""
    with open(DATA_DIR / 'curated_topics.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# Global data structures
SHLOKAS = load_shlokas()
CURATED_TOPICS = load_curated_topics()
SHLOKA_LOOKUP = {s['shloka_id']: s for s in SHLOKAS}

# ============ Functions ============

def get_shloka_by_id(shloka_id: str) -> dict | None:
    """
    Get shloka by ID.

    Args:
        shloka_id: Shloka ID like '2.47'

    Returns:
        Shloka dict or None if not found
    """
    return SHLOKA_LOOKUP.get(shloka_id)

def get_daily_shloka(topic: str = None) -> dict:
    """
    Get daily shloka (personalized by topic if provided).

    Args:
        topic: Topic key (chinta, krodh, etc.) or None

    Returns:
        Random shloka dict from topic's best shlokas or famous shlokas
    """
    if topic and topic in CURATED_TOPICS:
        # Get from topic's best shlokas
        shloka_ids = CURATED_TOPICS[topic]['best_shlokas']
        shloka_id = random.choice(shloka_ids)
        return SHLOKA_LOOKUP.get(shloka_id, random.choice(SHLOKAS))

    # Default to famous shlokas
    shloka_id = random.choice(FAMOUS_SHLOKA_IDS)
    return SHLOKA_LOOKUP.get(shloka_id, random.choice(SHLOKAS))

def get_shlokas_by_ids(shloka_ids: list[str]) -> list[dict]:
    """
    Get multiple shlokas by IDs.

    Args:
        shloka_ids: List of shloka IDs

    Returns:
        List of shloka dicts
    """
    return [SHLOKA_LOOKUP[sid] for sid in shloka_ids if sid in SHLOKA_LOOKUP]
```

**Create __init__.py for models package:**
```bash
mkdir -p models
touch models/__init__.py
```

---

### PHASE 3: Services (6 hours)

#### 3.1 services/search.py - Semantic Search

**File:** `services/search.py`

```python
"""
Shloka search service.
Semantic search using ChromaDB + Cohere, with keyword fallback.
"""

import logging
import cohere
import chromadb
from config import (
    COHERE_API_KEY, CHROMADB_PATH, COHERE_MODEL,
    CHROMADB_COLLECTION, SEARCH_RESULTS_DEFAULT
)
from models.shloka import SHLOKAS, SHLOKA_LOOKUP, CURATED_TOPICS

# ============ Semantic Search Class ============

class SemanticSearch:
    """Semantic search using Cohere embeddings and ChromaDB."""

    def __init__(self):
        """Lazy initialization - only initialize when first used."""
        self.collection = None
        self.cohere_client = None

    def _init_lazy(self):
        """Initialize ChromaDB and Cohere client (called on first search)."""
        if self.collection is not None:
            return

        try:
            # Initialize Cohere
            self.cohere_client = cohere.Client(COHERE_API_KEY)

            # Initialize ChromaDB
            chroma_client = chromadb.PersistentClient(path=str(CHROMADB_PATH))
            self.collection = chroma_client.get_collection(name=CHROMADB_COLLECTION)

            logging.info("SemanticSearch initialized successfully")
        except Exception as e:
            logging.error(f"SemanticSearch initialization failed: {e}")
            self.collection = None

    def search(self, query: str, n_results: int = 3) -> list[str]:
        """
        Search for shlokas using semantic similarity.

        Args:
            query: User's question
            n_results: Number of results to return

        Returns:
            List of shloka IDs (e.g., ['2.47', '3.8'])
        """
        self._init_lazy()

        if self.collection is None or self.cohere_client is None:
            return []

        try:
            # Get query embedding
            response = self.cohere_client.embed(
                texts=[query],
                model=COHERE_MODEL,
                input_type='search_query'
            )
            query_embedding = response.embeddings[0]

            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )

            # Extract shloka IDs from metadata
            if results['ids'] and len(results['ids']) > 0:
                shloka_ids = results['ids'][0]
                logging.info(f"Semantic search for '{query[:50]}': {len(shloka_ids)} results")
                return shloka_ids

            return []

        except Exception as e:
            logging.error(f"Semantic search error: {e}")
            return []

# Global semantic search instance
semantic_search = SemanticSearch()

# ============ Topic Detection ============

# Topic keywords for keyword-based search
USER_QUERY_TOPICS = {
    'karma': ['काम', 'कर्म', 'करना', 'कर्तव्य', 'जिम्मेदारी', 'duty', 'work', 'action'],
    'krodh': ['गुस्सा', 'क्रोध', 'anger', 'angry', 'irritation'],
    'bhay': ['डर', 'भय', 'fear', 'scared', 'afraid'],
    'chinta': ['चिंता', 'anxiety', 'worried', 'tension'],
    'shanti': ['शांति', 'peace', 'calm', 'tranquil'],
    'dukh': ['दुख', 'suffering', 'pain', 'sorrow'],
    'mrityu': ['मृत्यु', 'मौत', 'death', 'died'],
}

def detect_topics(query: str) -> list[str]:
    """
    Detect topics in query using keyword matching.

    Args:
        query: User's question

    Returns:
        List of detected topic keys
    """
    query_lower = query.lower()
    detected = []

    for topic, keywords in USER_QUERY_TOPICS.items():
        if any(kw in query_lower for kw in keywords):
            detected.append(topic)

    return detected

# ============ Main Search Function ============

def find_relevant_shlokas(query: str, max_results: int = SEARCH_RESULTS_DEFAULT) -> list[dict]:
    """
    Find relevant shlokas using semantic search + keyword fallback.

    Search strategy:
    1. Try semantic search first (ChromaDB + Cohere)
    2. If no results, try curated topics keyword matching
    3. If still no results, return famous shlokas

    Args:
        query: User's question
        max_results: Maximum number of shlokas to return (default: 1 for v1)

    Returns:
        List of shloka dicts
    """
    results = []

    # Step 1: Semantic search
    shloka_ids = semantic_search.search(query, n_results=max_results * 2)
    if shloka_ids:
        results = [SHLOKA_LOOKUP[sid] for sid in shloka_ids if sid in SHLOKA_LOOKUP]
        if results:
            logging.info(f"Found {len(results)} shlokas via semantic search")
            return results[:max_results]

    # Step 2: Curated topics keyword matching
    query_lower = query.lower()
    for topic_key, topic_data in CURATED_TOPICS.items():
        keywords = topic_data.get('keywords', [])
        if any(kw.lower() in query_lower for kw in keywords):
            shloka_ids = topic_data['best_shlokas'][:max_results]
            results = [SHLOKA_LOOKUP[sid] for sid in shloka_ids if sid in SHLOKA_LOOKUP]
            if results:
                logging.info(f"Found {len(results)} shlokas via topic: {topic_key}")
                return results

    # Step 3: Topic detection fallback
    detected_topics = detect_topics(query)
    if detected_topics:
        # Map detected topics to curated topics
        topic_mapping = {
            'bhay': 'chinta',
            'chinta': 'chinta',
            'krodh': 'krodh',
            'karma': 'kartavya',
            'dukh': 'dukh',
            'mrityu': 'dukh',
            'shanti': 'chinta'
        }

        for detected in detected_topics:
            curated_topic = topic_mapping.get(detected)
            if curated_topic and curated_topic in CURATED_TOPICS:
                shloka_ids = CURATED_TOPICS[curated_topic]['best_shlokas'][:max_results]
                results = [SHLOKA_LOOKUP[sid] for sid in shloka_ids if sid in SHLOKA_LOOKUP]
                if results:
                    logging.info(f"Found {len(results)} shlokas via detected topic: {detected}")
                    return results

    # Step 4: Universal shlokas (last resort)
    from config import FAMOUS_SHLOKA_IDS
    default_ids = FAMOUS_SHLOKA_IDS[:max_results]
    results = [SHLOKA_LOOKUP[sid] for sid in default_ids if sid in SHLOKA_LOOKUP]

    logging.info(f"Returning {len(results)} default shlokas")
    return results
```

---

#### 3.2 services/ai_interpretation.py - Gemini AI

**File:** `services/ai_interpretation.py`

```python
"""
AI interpretation service using Google Gemini.
Generates contextual Hindi explanations connecting shlokas to user questions.
"""

import logging
import google.generativeai as genai
from config import GOOGLE_API_KEY, GEMINI_MODEL, AI_INTERPRETATION_MAX_LENGTH

# ============ AI Interpretation ============

def get_ai_interpretation(user_query: str, shlokas: list[dict]) -> str:
    """
    Use Gemini 2.5 Flash for contextual interpretation.

    Args:
        user_query: User's question
        shlokas: List of relevant shloka dicts

    Returns:
        3-4 line Hindi explanation or empty string on failure
    """
    if not GOOGLE_API_KEY:
        logging.warning("GOOGLE_API_KEY not set, skipping AI interpretation")
        return ""

    if not shlokas:
        return ""

    try:
        # Configure Gemini
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel(GEMINI_MODEL)

        # Build shloka context
        shloka_context = "\n\n".join([
            f"श्लोक {s['shloka_id']}:\n{s['sanskrit']}\nअर्थ: {s['hindi_meaning'][:AI_INTERPRETATION_MAX_LENGTH]}"
            for s in shlokas
        ])

        # Prompt template (empathy-first, Hindi-focused, elderly-friendly)
        prompt = f"""आप एक गीता विशेषज्ञ हैं। उपयोगकर्ता का प्रश्न है: "{user_query}"

निम्नलिखित श्लोक इस प्रश्न से संबंधित हैं:

{shloka_context}

कृपया बहुत सरल हिंदी में (जो बुज़ुर्ग समझ सकें) बताएं कि ये श्लोक उनकी स्थिति पर कैसे लागू होते हैं।

दिशा-निर्देश:
- केवल 3-4 वाक्यों में संक्षेप में बताएं
- कठिन या संस्कृत शब्दों का प्रयोग न करें
- सीधी सलाह न दें, केवल गीता का संदर्भ दें
- सहानुभूतिपूर्ण स्वर रखें"""

        # Generate response
        response = model.generate_content(prompt)
        interpretation = response.text.strip()

        logging.info(f"AI interpretation generated for query: {user_query[:50]}")
        return interpretation

    except Exception as e:
        logging.error(f"Gemini AI error: {e}")
        return ""
```

---

#### 3.3 services/session.py - SQLite Session Management

**File:** `services/session.py`

```python
"""
User session management using SQLite.
Stores conversation context, last shlokas, topic engagement.
"""

import sqlite3
import json
import logging
from datetime import datetime
from config import DB_PATH

# ============ Session CRUD ============

def get_session(user_id: str) -> dict:
    """
    Get user session from SQLite.
    Creates new session if doesn't exist.

    Args:
        user_id: Telegram user ID (string)

    Returns:
        Session dict with keys: user_id, last_shlokas, last_query, context, top_topics
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM sessions WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()

    if row:
        conn.close()
        return {
            'user_id': row[0],
            'last_shlokas': json.loads(row[1]) if row[1] else [],
            'last_query': row[2] or '',
            'context': row[3],
            'top_topics': json.loads(row[4]) if row[4] else {},
            'created_at': row[5],
            'updated_at': row[6]
        }

    # Create new session
    now = datetime.now().isoformat()
    cursor.execute('''
        INSERT INTO sessions (user_id, last_shlokas, last_query, context, top_topics, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, '[]', '', None, '{}', now, now))
    conn.commit()
    conn.close()

    logging.info(f"Created new session for user: {user_id}")

    return {
        'user_id': user_id,
        'last_shlokas': [],
        'last_query': '',
        'context': None,
        'top_topics': {},
        'created_at': now,
        'updated_at': now
    }

def save_session(user_id: str, data: dict):
    """
    Save/update user session in SQLite.

    Args:
        user_id: Telegram user ID
        data: Session dict to save
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE sessions
        SET last_shlokas = ?,
            last_query = ?,
            context = ?,
            top_topics = ?,
            updated_at = ?
        WHERE user_id = ?
    ''', (
        json.dumps(data.get('last_shlokas', [])),
        data.get('last_query', ''),
        data.get('context'),
        json.dumps(data.get('top_topics', {})),
        datetime.now().isoformat(),
        user_id
    ))

    conn.commit()
    conn.close()

def update_top_topics(user_id: str, topic: str):
    """
    Increment topic engagement counter for personalization.

    Args:
        user_id: Telegram user ID
        topic: Topic key (chinta, krodh, etc.)
    """
    session = get_session(user_id)
    top_topics = session.get('top_topics', {})

    # Increment counter
    top_topics[topic] = top_topics.get(topic, 0) + 1

    session['top_topics'] = top_topics
    save_session(user_id, session)

    logging.info(f"Updated top topics for {user_id}: {top_topics}")
```

---

#### 3.4 services/formatter.py - Telegram Response Formatting

**File:** `services/formatter.py`

```python
"""
Response formatting service for Telegram.
Forward-friendly formatting with "गीता GPT 🙏" footer.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import TOPIC_MENU

# ============ Shloka Formatting ============

def format_shloka(shloka: dict, interpretation: str = "") -> str:
    """
    Format single shloka for Telegram (forward-friendly).

    Format:
    📿 गीता 2.47

    कर्मण्येवाधिकारस्ते...

    💡 [Hindi meaning - first 400 chars]

    [AI interpretation - 3-4 lines]

    — गीता GPT 🙏

    Args:
        shloka: Shloka dict
        interpretation: AI-generated interpretation (optional)

    Returns:
        Formatted message string
    """
    response = f"📿 गीता {shloka['shloka_id']}\n\n"

    # Sanskrit text
    response += f"{shloka['sanskrit']}\n\n"

    # Hindi meaning (truncate to 400 chars)
    meaning = shloka['hindi_meaning']
    if len(meaning) > 400:
        meaning = meaning[:400] + '...'
    response += f"💡 {meaning}\n\n"

    # AI interpretation
    if interpretation:
        response += f"{interpretation}\n\n"

    # Footer (for forwarding branding)
    response += "— गीता GPT 🙏"

    return response

# ============ Command Responses ============

def format_welcome() -> str:
    """Welcome message for /start."""
    return """🙏 गीता GPT में स्वागत है!

जीवन का कोई भी प्रश्न पूछें — गीता से उत्तर मिलेगा।

रोज़ सुबह 6 बजे प्रेरणादायक श्लोक आएगा।
बंद करने के लिए "रोकें" भेजें।

विषय देखने के लिए "विषय" भेजें।
मदद के लिए "मदद" भेजें।"""

def format_help() -> str:
    """Help message."""
    return """🙏 गीता GPT - सहायता

📝 आप क्या कर सकते हैं:

• कोई भी प्रश्न पूछें
  "मुझे गुस्सा आता है"
  "मन शांत कैसे करें"

• विषय - विषयों की सूची
• प्रेरणा - आज का श्लोक
• और - अगला श्लोक
• रोकें - रोज़ का श्लोक बंद करें

बस अपनी बात लिखें या बोलें (voice note)।"""

# ============ Topic Menu ============

def format_topic_menu() -> tuple[str, InlineKeyboardMarkup]:
    """
    Create Telegram inline keyboard for topic menu.

    Returns:
        Tuple of (message_text, keyboard_markup)
    """
    text = "विषय चुनें:"

    keyboard = [
        [InlineKeyboardButton(TOPIC_MENU['chinta'], callback_data='topic_chinta')],
        [InlineKeyboardButton(TOPIC_MENU['krodh'], callback_data='topic_krodh')],
        [InlineKeyboardButton(TOPIC_MENU['kartavya'], callback_data='topic_kartavya')],
        [InlineKeyboardButton(TOPIC_MENU['dukh'], callback_data='topic_dukh')],
        [InlineKeyboardButton(TOPIC_MENU['akela'], callback_data='topic_akela')]
    ]

    markup = InlineKeyboardMarkup(keyboard)
    return text, markup

# ============ Daily Shloka ============

def format_daily_shloka(shloka: dict) -> str:
    """
    Format daily shloka push message.

    Args:
        shloka: Shloka dict

    Returns:
        Formatted daily message
    """
    # Day names in Hindi
    days_hi = ['सोमवार', 'मंगलवार', 'बुधवार', 'गुरुवार', 'शुक्रवार', 'शनिवार', 'रविवार']

    from datetime import datetime
    day_name = days_hi[datetime.now().weekday()]

    response = f"🌅 {day_name} का गीता श्लोक\n\n"
    response += format_shloka(shloka)

    return response
```

---

#### 3.5 services/voice.py - Google Speech-to-Text

**File:** `services/voice.py`

```python
"""
Voice transcription service using Google Speech-to-Text.
Converts Telegram voice notes (Hindi) to text.
"""

import os
import logging
from google.cloud import speech_v1
from config import GOOGLE_API_KEY

# ============ Voice Transcription ============

def transcribe_voice(file_path: str) -> str | None:
    """
    Transcribe Telegram voice note using Google STT.

    Args:
        file_path: Path to downloaded .ogg voice file

    Returns:
        Transcribed Hindi text or None on failure
    """
    if not GOOGLE_API_KEY:
        logging.error("GOOGLE_API_KEY not set for voice transcription")
        return None

    try:
        # Set credentials (if using service account JSON)
        # For API key, Gemini and STT share the same key
        # Note: You may need to set up credentials differently
        # os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = GOOGLE_API_KEY

        client = speech_v1.SpeechClient()

        # Read audio file
        with open(file_path, 'rb') as audio_file:
            content = audio_file.read()

        audio = speech_v1.RecognitionAudio(content=content)

        # Configure recognition
        config = speech_v1.RecognitionConfig(
            encoding=speech_v1.RecognitionConfig.AudioEncoding.OGG_OPUS,
            sample_rate_hertz=48000,  # Telegram voice notes are 48kHz
            language_code='hi-IN',    # Hindi (India)
            enable_automatic_punctuation=True
        )

        # Perform recognition
        response = client.recognize(config=config, audio=audio)

        # Extract transcript
        if response.results:
            transcript = response.results[0].alternatives[0].transcript
            logging.info(f"Voice transcription successful: {transcript[:100]}")
            return transcript

        logging.warning("Voice transcription returned no results")
        return None

    except Exception as e:
        logging.error(f"Voice transcription error: {e}")
        return None
```

**Note:** Google Speech-to-Text requires proper authentication. You may need to:
1. Create a service account in Google Cloud Console
2. Download JSON key file
3. Set `GOOGLE_APPLICATION_CREDENTIALS` environment variable

For testing, you can use Gemini API key, but production should use proper service account.

---

#### 3.6 services/daily.py - Daily Shloka Push

**File:** `services/daily.py`

```python
"""
Daily shloka push service.
Manages subscribers and sends personalized daily shlokas.
"""

import sqlite3
import logging
from telegram import Bot
from config import TELEGRAM_BOT_TOKEN, DB_PATH
from models.shloka import get_daily_shloka
from services.formatter import format_daily_shloka
from services.session import get_session

# ============ Subscription Management ============

def subscribe(user_id: str):
    """
    Subscribe user to daily push.

    Args:
        user_id: Telegram user ID
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT OR REPLACE INTO subscribers (user_id, active)
        VALUES (?, 1)
    ''', (user_id,))

    conn.commit()
    conn.close()

    logging.info(f"User {user_id} subscribed to daily push")

def unsubscribe(user_id: str):
    """
    Unsubscribe user from daily push.

    Args:
        user_id: Telegram user ID
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE subscribers
        SET active = 0
        WHERE user_id = ?
    ''', (user_id,))

    conn.commit()
    conn.close()

    logging.info(f"User {user_id} unsubscribed from daily push")

# ============ Daily Push ============

def send_daily_push() -> tuple[int, int]:
    """
    Send daily shloka to all active subscribers.
    Personalized by user's top engaged topics.

    Returns:
        Tuple of (success_count, failure_count)
    """
    bot = Bot(token=TELEGRAM_BOT_TOKEN)

    # Get all active subscribers
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM subscribers WHERE active = 1')
    subscribers = [row[0] for row in cursor.fetchall()]
    conn.close()

    logging.info(f"Starting daily push to {len(subscribers)} subscribers")

    success_count = 0
    failure_count = 0

    for user_id in subscribers:
        try:
            # Get user's top engaged topic for personalization
            session = get_session(user_id)
            top_topics = session.get('top_topics', {})

            # Find most engaged topic
            top_topic = None
            if top_topics:
                top_topic = max(top_topics, key=top_topics.get)
                logging.info(f"User {user_id} top topic: {top_topic}")

            # Get personalized shloka
            shloka = get_daily_shloka(topic=top_topic)
            message = format_daily_shloka(shloka)

            # Send message
            bot.send_message(chat_id=user_id, text=message)
            success_count += 1

        except Exception as e:
            logging.error(f"Daily push failed for user {user_id}: {e}")
            failure_count += 1

    logging.info(f"Daily push complete: {success_count} sent, {failure_count} failed")
    return success_count, failure_count
```

**Create __init__.py for services package:**
```bash
mkdir -p services
touch services/__init__.py
```

---

### PHASE 4: Guardrails (2 hours)

#### 4.1 guardrails/rate_limiter.py

**File:** `guardrails/rate_limiter.py`

```python
"""
Rate limiting guardrail using SQLite.
Limits users to 20 messages per hour.
"""

import sqlite3
import logging
from datetime import datetime
from config import RATE_LIMIT, RATE_WINDOW, DB_PATH

def check_rate_limit(user_id: str) -> bool:
    """
    Check if user has exceeded rate limit.

    Args:
        user_id: Telegram user ID

    Returns:
        True if OK to proceed, False if rate limited
    """
    now = datetime.now().timestamp()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Clean old messages (older than RATE_WINDOW)
    cursor.execute('''
        DELETE FROM messages
        WHERE user_id = ? AND sent_at < ?
    ''', (user_id, now - RATE_WINDOW))

    # Count recent messages
    cursor.execute('''
        SELECT COUNT(*) FROM messages
        WHERE user_id = ? AND sent_at >= ?
    ''', (user_id, now - RATE_WINDOW))

    count = cursor.fetchone()[0]

    if count >= RATE_LIMIT:
        conn.close()
        logging.warning(f"Rate limit exceeded for user {user_id}: {count}/{RATE_LIMIT}")
        return False

    # Add current message
    cursor.execute('''
        INSERT INTO messages (user_id, sent_at)
        VALUES (?, ?)
    ''', (user_id, now))

    conn.commit()
    conn.close()

    return True
```

---

#### 4.2 guardrails/content_filter.py

**File:** `guardrails/content_filter.py`

```python
"""
Content filtering guardrail.
Blocks profanity, manipulation attempts, and off-topic content.
"""

import logging
from config import BLOCKED_WORDS, MANIPULATION_PATTERNS, OFFTOPIC_KEYWORDS

def check_content(message: str) -> tuple[bool, str]:
    """
    Check message for inappropriate content.

    Args:
        message: User's message

    Returns:
        Tuple of (is_ok, reason)
        - is_ok: True if message is OK, False if blocked
        - reason: 'profanity' | 'manipulation' | 'offtopic' | ''
    """
    msg_lower = message.lower()

    # Check profanity (Hindi Devanagari + Hinglish + English)
    for word in BLOCKED_WORDS:
        if word.lower() in msg_lower:
            logging.warning(f"Blocked profanity: {word}")
            return False, 'profanity'

    # Check manipulation/jailbreak attempts
    for pattern in MANIPULATION_PATTERNS:
        if pattern.lower() in msg_lower:
            logging.warning(f"Blocked manipulation: {pattern}")
            return False, 'manipulation'

    # Check off-topic (politics, explicit)
    for keyword in OFFTOPIC_KEYWORDS:
        if keyword.lower() in msg_lower:
            logging.warning(f"Blocked off-topic: {keyword}")
            return False, 'offtopic'

    return True, ''
```

---

#### 4.3 guardrails/sanitizer.py

**File:** `guardrails/sanitizer.py`

```python
"""
Input sanitization guardrail.
Validates and cleans user input.
"""

from config import MAX_INPUT_LENGTH, MIN_INPUT_LENGTH

def sanitize_input(message: str) -> str:
    """
    Sanitize user input.

    - Limit to MAX_INPUT_LENGTH characters
    - Strip excessive whitespace

    Args:
        message: User's message

    Returns:
        Sanitized message
    """
    # Limit length
    message = message[:MAX_INPUT_LENGTH]

    # Strip excessive whitespace
    message = ' '.join(message.split())

    return message

def is_valid_input(message: str) -> bool:
    """
    Check if message is valid (not empty/gibberish).

    Args:
        message: Sanitized message

    Returns:
        True if valid, False otherwise
    """
    return message and len(message) >= MIN_INPUT_LENGTH
```

**Create __init__.py for guardrails package:**
```bash
mkdir -p guardrails
touch guardrails/__init__.py
```

---

## 5. Code Templates

### Complete implementation templates for all 17 files are provided above in Phases 1-4.

### Key files to review before proceeding:
1. `curated_topics.json` - 5-topic consolidation
2. `config.py` - All configuration
3. `services/search.py` - Semantic search logic
4. `services/formatter.py` - Telegram-specific formatting
5. `routes/telegram.py` - Main webhook handler (see Phase 5 below)

---

## 6. Testing Guide

### Manual Testing Checklist

**Setup:**
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Initialize database
python scripts/setup_db.py

# 3. Run Flask app
python app.py
```

**Test Cases:**

| # | Action | Expected Result |
|---|--------|-----------------|
| 1 | Send `/start` | Welcome message + auto-subscribed |
| 2 | Send `मदद` | Help message with commands |
| 3 | Send `विषय` | Inline keyboard with 5 topics |
| 4 | Click "मुझे चिंता/डर लगता है" | Relevant shloka + AI interpretation |
| 5 | Send "मुझे गुस्सा आता है" | Shloka about anger + interpretation |
| 6 | Send `और` | Next related shloka |
| 7 | Send voice note (Hindi) | Transcribed + answered |
| 8 | Send 25+ messages rapidly | "कृपया थोड़ा रुकें..." |
| 9 | Send profanity | "कृपया शालीन भाषा..." |
| 10 | Send "ignore previous" | "केवल गीता के ज्ञान..." |
| 11 | Send `रोकें` | Unsubscribed confirmation |
| 12 | Trigger /daily-push | All subscribers receive shloka |

### Unit Tests

Create `tests/` directory with:

**tests/test_search.py:**
```python
from services.search import find_relevant_shlokas

def test_semantic_search():
    results = find_relevant_shlokas("मुझे गुस्सा आता है")
    assert len(results) >= 1
    assert results[0]['shloka_id'] in ['2.62', '2.63', '3.37']
```

**tests/test_guardrails.py:**
```python
from guardrails.content_filter import check_content
from guardrails.sanitizer import sanitize_input, is_valid_input

def test_profanity_filter():
    is_ok, reason = check_content("भड़वा")
    assert is_ok == False
    assert reason == 'profanity'

def test_sanitizer():
    result = sanitize_input("  hello    world  ")
    assert result == "hello world"
```

---

## 7. Deployment Guide

### Update requirements.txt

```
flask>=3.0.0
gunicorn>=21.0.0
chromadb>=0.4.0
cohere>=5.0.0
google-generativeai>=0.5.0
google-cloud-speech>=2.20.0
python-telegram-bot>=13.15
```

### Create Procfile

```
web: gunicorn app:app
```

### Create railway.json

```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn app:app",
    "restartPolicyType": "ON_FAILURE"
  },
  "cron": [
    {
      "schedule": "30 0 * * *",
      "command": "curl -X POST -H 'X-Daily-Push-Secret: $DAILY_PUSH_SECRET' https://YOUR_APP.railway.app/daily-push"
    }
  ]
}
```

### Railway Deployment Steps

1. Push code to GitHub
2. Connect Railway to GitHub repo
3. Add environment variables in Railway dashboard:
   - `TELEGRAM_BOT_TOKEN`
   - `COHERE_API_KEY`
   - `GOOGLE_API_KEY`
   - `DAILY_PUSH_SECRET`
   - `PORT=5000`

4. Deploy

5. Set Telegram webhook:
```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://YOUR_APP.railway.app/webhook"
```

---

## Summary

**Estimated Implementation Time:** 20 hours

**Critical Path:**
1. Phase 1: Data + DB (2h)
2. Phase 2: Config + Models (1h)
3. Phase 3: Services (6h) - **Most complex**
4. Phase 4: Guardrails (2h)
5. Phase 5: Routes (4h) - **Core Telegram logic**
6. Phase 6: App Entry (0.5h)
7. Phase 7: Deploy (1h)
8. Phase 8: Testing (3h)

**Next Steps:**
1. Update `curated_topics.json` (5 topics)
2. Run `python scripts/setup_db.py`
3. Implement services (reuse WhatsApp logic)
4. Build Telegram webhook handler
5. Test locally
6. Deploy to Railway

Good luck! 🚀
