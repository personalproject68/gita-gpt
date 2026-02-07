"""REST API routes."""

import os
import logging
from flask import Blueprint, request, jsonify
from services.search import find_relevant_shlokas
from services.ai_interpretation import get_ai_interpretation
from services.daily import send_daily_push
from models.shloka import SHLOKA_LOOKUP, get_daily_shloka
from services.formatter import format_daily_shloka
from config import DAILY_PUSH_SECRET

logger = logging.getLogger('gitagpt.api')

bp = Blueprint('api', __name__)


@bp.route('/ask', methods=['GET'])
def ask():
    """Answer a question with relevant shlokas."""
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'Please provide ?q=your question'}), 400

    shlokas = find_relevant_shlokas(query)
    interpretation = get_ai_interpretation(query, shlokas[:1]) if shlokas else ''

    return jsonify({
        'query': query,
        'shlokas': [{
            'shloka_id': s['shloka_id'],
            'sanskrit': s['sanskrit'],
            'hindi_meaning': s['hindi_meaning'][:500],
        } for s in shlokas],
        'interpretation': interpretation,
    })


@bp.route('/daily-push', methods=['POST'])
def daily_push():
    """Trigger daily push to all subscribers. Requires secret key."""
    secret = request.headers.get('X-Push-Secret') or request.args.get('secret')

    if not DAILY_PUSH_SECRET or secret != DAILY_PUSH_SECRET:
        return jsonify({'error': 'Unauthorized'}), 401

    sent, failed = send_daily_push()
    return jsonify({'sent': sent, 'failed': failed})


@bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok', 'service': 'GitaGPT'})


@bp.route('/shloka/<shloka_id>', methods=['GET'])
def get_shloka(shloka_id: str):
    """Get a specific shloka by ID."""
    shloka = SHLOKA_LOOKUP.get(shloka_id)
    if not shloka:
        return jsonify({'error': f'Shloka {shloka_id} not found'}), 404

    return jsonify({
        'shloka_id': shloka_id,
        'sanskrit': shloka['sanskrit'],
        'hindi_meaning': shloka['hindi_meaning'],
        'tags': shloka.get('tags', []),
    })
