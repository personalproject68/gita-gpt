#!/usr/bin/env python3
"""Gita Sarathi - Telegram Bot & PWA for Bhagavad Gita guidance."""

import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from config import PORT, DB_PATH
from scripts.setup_db import setup_database

# Initialize database on startup
if not DB_PATH.exists():
    setup_database()

app = Flask(__name__)

# Register blueprints
from routes.telegram import bp as telegram_bp
from routes.api import bp as api_bp
from routes.web import bp as web_bp

app.register_blueprint(telegram_bp)
app.register_blueprint(api_bp)
app.register_blueprint(web_bp)

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=PORT, debug=debug_mode)
