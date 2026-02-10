"""Gita Sarathi Configuration - All settings and constants."""

import os
import logging
from pathlib import Path

# Environment
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
COHERE_API_KEY = os.environ.get('COHERE_API_KEY')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
DAILY_PUSH_SECRET = os.environ.get('DAILY_PUSH_SECRET')
ADMIN_USER_ID = os.environ.get('ADMIN_USER_ID', '598684231')
MSG91_AUTH_KEY = os.environ.get('MSG91_AUTH_KEY')
MSG91_TEMPLATE_ID = os.environ.get('MSG91_TEMPLATE_ID')
PORT = int(os.environ.get('PORT', 5000))

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'
DB_PATH = BASE_DIR / 'gitagpt.db'
CHROMADB_PATH = DATA_DIR / 'chromadb_mvp'

# Rate limiting
RATE_LIMIT = 20
RATE_WINDOW = 3600  # 1 hour in seconds

# Guardrails - blocked words (Hindi + Hinglish + English)
BLOCKED_WORDS = [
    'भड़वा', 'रंडी', 'चूतिया', 'मादरचोद', 'बहनचोद', 'गांड', 'लौड़ा', 'भोसड़ी',
    'fuck', 'shit', 'ass', 'bitch', 'bastard', 'dick', 'pussy',
]

MANIPULATION_PATTERNS = [
    'ignore previous', 'forget instructions', 'you are now', 'act as',
    'pretend to be', 'bypass', 'ignore all', 'disregard', 'new persona',
    'jailbreak', 'dan mode', 'developer mode', 'ignore safety',
]

OFFTOPIC_KEYWORDS = [
    'modi', 'rahul', 'bjp', 'congress', 'election', 'vote', 'pakistan',
    'muslim', 'hindu', 'christian', 'sex', 'porn', 'nude', 'xxx',
]

# Telegram topic menu (5 v1 topics)
TOPIC_MENU = {
    'chinta': 'मुझे चिंता/डर लगता है',
    'krodh': 'मुझे गुस्सा आता है',
    'kartavya': 'मुझे समझ नहीं आता क्या करूं',
    'dukh': 'मैं बीमार हूं / कोई खो दिया',
    'akela': 'मैं अकेला महसूस करता हूं',
}

# अमृत श्लोक — 10 most iconic Gita shlokas
AMRIT_SHLOKAS = [
    ('2.47', 'कर्मण्येवाधिकारस्ते'),
    ('4.7', 'यदा यदा ही धर्मस्य'),
    ('2.20', 'न जायते म्रियते वा'),
    ('9.22', 'अनन्याश्चिन्तयन्तो माम्'),
    ('18.66', 'सर्वधर्मान्परित्यज्य'),
    ('2.14', 'मात्रास्पर्शास्तु कौन्तेय'),
    ('3.21', 'यद्यदाचरति श्रेष्ठः'),
    ('6.5', 'उद्धरेदात्मनात्मानम्'),
    ('11.32', 'कालोऽस्मि लोकक्षयकृत्'),
    ('2.3', 'क्लैब्यं मा स्म गमः पार्थ'),
]

# Logging
logging.basicConfig(
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger('gitagpt')
