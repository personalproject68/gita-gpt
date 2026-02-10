"""REST API routes."""

import os
import logging
from flask import Blueprint, request, jsonify
from services.search import find_relevant_shlokas
from services.ai_interpretation import get_ai_interpretation, get_contextual_interpretation
from services.daily import send_daily_push
from guardrails.content_filter import check_content
from guardrails.sanitizer import sanitize_input, is_valid_input
from models.shloka import (
    SHLOKA_LOOKUP, COMPLETE_LOOKUP, COMPLETE_SHLOKAS, CHAPTER_NAMES,
    get_daily_shloka, get_journey_shloka, get_chapter_info, is_chapter_complete,
)
from services.formatter import format_daily_shloka
from config import DAILY_PUSH_SECRET, AMRIT_SHLOKAS, TOPIC_MENU, DATA_DIR

logger = logging.getLogger('gitagpt.api')

bp = Blueprint('api', __name__)

# Simple in-memory rate limiter for web API (no SQLite dependency)
import time as _time
_web_rate_limits: dict[str, list[float]] = {}
_WEB_RATE_LIMIT = 20
_WEB_RATE_WINDOW = 3600  # 1 hour


def _check_web_rate_limit(client_ip: str) -> bool:
    """Return True if within limit, False if rate limited."""
    now = _time.time()
    cutoff = now - _WEB_RATE_WINDOW
    timestamps = _web_rate_limits.get(client_ip, [])
    timestamps = [t for t in timestamps if t > cutoff]
    if len(timestamps) >= _WEB_RATE_LIMIT:
        _web_rate_limits[client_ip] = timestamps
        return False
    timestamps.append(now)
    _web_rate_limits[client_ip] = timestamps
    return True


@bp.route('/ask', methods=['GET'])
def ask():
    """Answer a question with relevant shlokas."""
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'Please provide ?q=your question'}), 400

    # Sanitize + validate
    query = sanitize_input(query)
    if not is_valid_input(query):
        return jsonify({'error': 'कृपया अपना प्रश्न विस्तार से लिखें।'}), 400

    # Content filter (profanity, manipulation, off-topic)
    is_ok, reason = check_content(query)
    if not is_ok:
        return jsonify({
            'query': query,
            'shlokas': [],
            'interpretation': '',
            'filtered': reason,
            'message': 'आपके मन में कुछ कठिन भाव हैं। क्या मैं गीता का मार्गदर्शन दूं?',
        })

    # IP-based rate limiting for web (simple in-memory)
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr or 'unknown')
    client_ip = client_ip.split(',')[0].strip()
    if not _check_web_rate_limit(client_ip):
        return jsonify({
            'error': 'कृपया थोड़ा रुकें, बहुत तेज़ी से प्रश्न आ रहे हैं।',
            'rate_limited': True,
        }), 429

    shlokas = find_relevant_shlokas(query)

    # Try Gemini contextual interpretation (query-specific margdarshan)
    # Fall back to pre-fetched interpretation if Gemini unavailable
    interpretation = ''
    if shlokas:
        interpretation = get_contextual_interpretation(query, shlokas[:1])
        if not interpretation:
            interpretation = get_ai_interpretation(query, shlokas[:1])

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
    return jsonify({'status': 'ok', 'service': 'Gita Sarathi'})


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


# --- PWA API Endpoints ---

def _load_interpretations():
    """Load pre-fetched interpretations."""
    import json
    path = DATA_DIR / 'interpretations.json'
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


# Cache interpretations at module level
_INTERPRETATIONS = None


def _get_interpretations():
    global _INTERPRETATIONS
    if _INTERPRETATIONS is None:
        _INTERPRETATIONS = _load_interpretations()
    return _INTERPRETATIONS


@bp.route('/api/amrit', methods=['GET'])
def amrit_shlokas():
    """Return the 10 iconic अमृत shlokas with interpretations."""
    interpretations = _get_interpretations()
    result = []
    for shloka_id, label in AMRIT_SHLOKAS:
        shloka = COMPLETE_LOOKUP.get(shloka_id) or SHLOKA_LOOKUP.get(shloka_id)
        if shloka:
            result.append({
                'shloka_id': shloka_id,
                'label': label,
                'sanskrit': shloka['sanskrit'],
                'hindi_meaning': shloka['hindi_meaning'],
                'interpretation': interpretations.get(shloka_id, ''),
            })
    return jsonify({'shlokas': result})


@bp.route('/api/topics', methods=['GET'])
def topics():
    """Return the 5 topic categories for the PWA."""
    result = []
    for key, label in TOPIC_MENU.items():
        result.append({
            'key': key,
            'label': label,
            'query': label,
        })
    return jsonify({'topics': result})


@bp.route('/api/journey', methods=['GET'])
def journey():
    """Return shloka at a given journey position with chapter info."""
    pos = request.args.get('pos', 0, type=int)
    pos = max(0, min(pos, len(COMPLETE_SHLOKAS) - 1))

    shloka = get_journey_shloka(pos)
    if not shloka:
        return jsonify({'error': 'Invalid position'}), 400

    interpretations = _get_interpretations()
    ch_info = get_chapter_info(pos)
    chapter_complete = is_chapter_complete(pos)

    # Build chapter map: for each chapter, how many shlokas and completion status
    chapter_map = []
    for ch in range(1, 19):
        from models.shloka import _CHAPTER_BOUNDS
        bounds = _CHAPTER_BOUNDS.get(ch, {})
        first = bounds.get('first', 0)
        last = bounds.get('last', 0)
        total = last - first + 1
        chapter_map.append({
            'chapter': ch,
            'name': CHAPTER_NAMES.get(ch, ''),
            'total': total,
            'first_pos': first,
            'last_pos': last,
        })

    return jsonify({
        'position': pos,
        'total_shlokas': len(COMPLETE_SHLOKAS),
        'shloka': {
            'shloka_id': shloka['shloka_id'],
            'sanskrit': shloka['sanskrit'],
            'hindi_meaning': shloka['hindi_meaning'],
            'interpretation': interpretations.get(shloka['shloka_id'], ''),
        },
        'chapter': {
            'number': ch_info['chapter'],
            'name': ch_info['name_hi'],
            'shloka_in_chapter': pos - ch_info['first_position'] + 1,
            'chapter_total': ch_info['last_position'] - ch_info['first_position'] + 1,
        },
        'chapter_complete': chapter_complete,
        'journey_complete': pos >= len(COMPLETE_SHLOKAS) - 1,
        'chapter_map': chapter_map,
    })
