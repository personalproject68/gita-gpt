"""Gita Sarathi — OTP Auth Service (MSG91 + SQLite)."""

import re
import secrets
import sqlite3
from datetime import datetime, timedelta

import requests

from config import DB_PATH, MSG91_AUTH_KEY, MSG91_TEMPLATE_ID, logger

OTP_RATE_LIMIT = 3          # max OTP sends per phone per hour
OTP_MAX_ATTEMPTS = 5         # max verification tries per OTP
OTP_EXPIRY_MINUTES = 5
SESSION_EXPIRY_DAYS = 90

log = logger.getChild('auth')


def _db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def clean_phone(raw: str) -> str | None:
    """Normalize Indian phone number → '919876543210' or None if invalid."""
    digits = re.sub(r'\D', '', raw)
    if digits.startswith('91') and len(digits) == 12:
        digits = digits[2:]
    if digits.startswith('+91'):
        digits = digits[3:]
    if len(digits) == 10 and digits[0] in '6789':
        return '91' + digits
    return None


def send_otp(phone_raw: str) -> dict:
    """Send OTP via MSG91. Returns {success, message} or {error}."""
    phone = clean_phone(phone_raw)
    if not phone:
        return {'error': 'सही मोबाइल नंबर डालें (10 अंक)', 'status': 400}

    conn = _db()
    try:
        # Rate limit check
        cutoff = (datetime.utcnow() - timedelta(hours=1)).isoformat()
        count = conn.execute(
            'SELECT COUNT(*) FROM otps WHERE phone = ? AND created_at > ?',
            (phone, cutoff)
        ).fetchone()[0]

        if count >= OTP_RATE_LIMIT:
            return {'error': 'बहुत बार OTP भेजा गया, 1 घंटे बाद कोशिश करें', 'status': 429}

        # Send via MSG91
        resp = requests.post(
            'https://control.msg91.com/api/v5/otp',
            headers={'authkey': MSG91_AUTH_KEY},
            json={
                'mobile': phone,
                'template_id': MSG91_TEMPLATE_ID,
                'otp_length': 4,
            },
            timeout=10,
        )
        data = resp.json()
        log.info(f'MSG91 send OTP response for {phone[-4:]}: {data.get("type")}')

        if data.get('type') == 'success':
            request_id = data.get('request_id', '')
            conn.execute(
                'INSERT INTO otps (phone, request_id) VALUES (?, ?)',
                (phone, request_id)
            )
            conn.commit()
            return {'success': True, 'message': f'OTP भेजा गया {phone_raw[-4:]} पर'}

        return {'error': 'OTP भेजने में समस्या, फिर कोशिश करें', 'status': 500}

    except requests.RequestException as e:
        log.error(f'MSG91 send error: {e}')
        return {'error': 'OTP भेजने में समस्या, फिर कोशिश करें', 'status': 500}
    finally:
        conn.close()


def verify_otp(phone_raw: str, otp: str) -> dict:
    """Verify OTP via MSG91. On success, create user + session token."""
    phone = clean_phone(phone_raw)
    if not phone:
        return {'error': 'सही मोबाइल नंबर डालें', 'status': 400}

    conn = _db()
    try:
        # Get latest OTP record
        row = conn.execute(
            'SELECT rowid, attempts, created_at FROM otps WHERE phone = ? ORDER BY created_at DESC LIMIT 1',
            (phone,)
        ).fetchone()

        if not row:
            return {'error': 'पहले OTP भेजें', 'status': 400}

        # Check expiry
        created = datetime.fromisoformat(row['created_at'])
        if datetime.utcnow() - created > timedelta(minutes=OTP_EXPIRY_MINUTES):
            return {'error': 'OTP समाप्त हो गया, नया OTP भेजें', 'status': 400}

        # Check attempts
        if row['attempts'] >= OTP_MAX_ATTEMPTS:
            return {'error': 'बहुत बार गलत OTP, नया OTP भेजें', 'status': 429}

        # Increment attempts
        conn.execute(
            'UPDATE otps SET attempts = attempts + 1 WHERE rowid = ?',
            (row['rowid'],)
        )
        conn.commit()

        # Verify via MSG91
        resp = requests.get(
            'https://control.msg91.com/api/v5/otp/verify',
            params={'mobile': phone, 'otp': otp},
            headers={'authkey': MSG91_AUTH_KEY},
            timeout=10,
        )
        data = resp.json()
        log.info(f'MSG91 verify response for {phone[-4:]}: {data.get("type")}')

        if data.get('type') != 'success':
            return {'error': 'गलत OTP, फिर कोशिश करें', 'status': 400}

        # OTP verified — create/get user
        user_id = f'ph_{phone}'
        user = conn.execute(
            'SELECT * FROM web_users WHERE user_id = ?', (user_id,)
        ).fetchone()

        if not user:
            conn.execute(
                'INSERT INTO web_users (user_id, phone) VALUES (?, ?)',
                (user_id, phone)
            )

        # Create session token
        token = secrets.token_hex(32)
        expires = (datetime.utcnow() + timedelta(days=SESSION_EXPIRY_DAYS)).isoformat()
        conn.execute(
            'INSERT INTO web_sessions (token, user_id, expires_at) VALUES (?, ?, ?)',
            (token, user_id, expires)
        )
        conn.commit()

        # Fetch user data
        user = conn.execute(
            'SELECT * FROM web_users WHERE user_id = ?', (user_id,)
        ).fetchone()

        return {
            'success': True,
            'token': token,
            'user': {
                'journey_position': user['journey_position'],
                'journey_streak': user['journey_streak'],
                'journey_last_date': user['journey_last_date'],
            }
        }

    except requests.RequestException as e:
        log.error(f'MSG91 verify error: {e}')
        return {'error': 'OTP जांच में समस्या, फिर कोशिश करें', 'status': 500}
    finally:
        conn.close()


def get_user_from_token(token: str) -> dict | None:
    """Look up session token → user. Returns user dict or None."""
    if not token:
        return None
    conn = _db()
    try:
        row = conn.execute(
            '''SELECT ws.user_id, ws.expires_at, wu.*
               FROM web_sessions ws
               JOIN web_users wu ON ws.user_id = wu.user_id
               WHERE ws.token = ?''',
            (token,)
        ).fetchone()
        if not row:
            return None
        if datetime.fromisoformat(row['expires_at']) < datetime.utcnow():
            conn.execute('DELETE FROM web_sessions WHERE token = ?', (token,))
            conn.commit()
            return None
        return dict(row)
    finally:
        conn.close()


def sync_journey(user_id: str, client_pos: int, client_streak: int, client_last_date: str | None) -> dict:
    """Sync journey progress — server keeps max(server, client)."""
    conn = _db()
    try:
        user = conn.execute(
            'SELECT * FROM web_users WHERE user_id = ?', (user_id,)
        ).fetchone()
        if not user:
            return {'error': 'User not found', 'status': 404}

        final_pos = max(user['journey_position'] or 0, client_pos or 0)
        final_streak = max(user['journey_streak'] or 0, client_streak or 0)
        final_date = client_last_date or user['journey_last_date']

        conn.execute(
            '''UPDATE web_users
               SET journey_position = ?, journey_streak = ?, journey_last_date = ?,
                   updated_at = CURRENT_TIMESTAMP
               WHERE user_id = ?''',
            (final_pos, final_streak, final_date, user_id)
        )
        conn.commit()

        return {
            'success': True,
            'journey_position': final_pos,
            'journey_streak': final_streak,
            'journey_last_date': final_date,
        }
    finally:
        conn.close()


def logout(token: str):
    """Delete session token."""
    conn = _db()
    try:
        conn.execute('DELETE FROM web_sessions WHERE token = ?', (token,))
        conn.commit()
    finally:
        conn.close()
