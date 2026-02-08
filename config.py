"""GitaGPT Configuration - All settings and constants."""

import os
import logging
from pathlib import Path

# Environment
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
COHERE_API_KEY = os.environ.get('COHERE_API_KEY')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
DAILY_PUSH_SECRET = os.environ.get('DAILY_PUSH_SECRET')
ADMIN_USER_ID = os.environ.get('ADMIN_USER_ID', '598684231')
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

# Logging
logging.basicConfig(
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger('gitagpt')
