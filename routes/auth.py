"""Gita Sarathi — Auth API Routes."""

from flask import Blueprint, request, jsonify, make_response

from services.auth import send_otp, verify_otp, get_user_from_token, sync_journey, logout, SESSION_EXPIRY_DAYS

bp = Blueprint('auth', __name__)


def _get_token():
    """Extract auth token from cookie or Authorization header."""
    token = request.cookies.get('gita_token')
    if not token:
        auth = request.headers.get('Authorization', '')
        if auth.startswith('Bearer '):
            token = auth[7:]
    return token


@bp.route('/api/auth/send-otp', methods=['POST'])
def api_send_otp():
    data = request.get_json(silent=True) or {}
    phone = data.get('phone', '').strip()
    if not phone:
        return jsonify({'error': 'मोबाइल नंबर डालें'}), 400

    result = send_otp(phone)
    status = result.pop('status', 200)
    return jsonify(result), status


@bp.route('/api/auth/verify-otp', methods=['POST'])
def api_verify_otp():
    data = request.get_json(silent=True) or {}
    phone = data.get('phone', '').strip()
    otp = data.get('otp', '').strip()
    if not phone or not otp:
        return jsonify({'error': 'मोबाइल नंबर और OTP डालें'}), 400

    result = verify_otp(phone, otp)
    status = result.pop('status', 200)

    if result.get('success'):
        resp = make_response(jsonify(result))
        resp.set_cookie(
            'gita_token',
            result['token'],
            max_age=SESSION_EXPIRY_DAYS * 86400,
            httponly=True,
            samesite='Lax',
            path='/',
        )
        return resp

    return jsonify(result), status


@bp.route('/api/auth/me')
def api_me():
    token = _get_token()
    user = get_user_from_token(token)
    if not user:
        return jsonify({'logged_in': False})
    return jsonify({
        'logged_in': True,
        'user': {
            'journey_position': user['journey_position'],
            'journey_streak': user['journey_streak'],
            'journey_last_date': user['journey_last_date'],
        }
    })


@bp.route('/api/auth/sync', methods=['POST'])
def api_sync():
    token = _get_token()
    user = get_user_from_token(token)
    if not user:
        return jsonify({'error': 'लॉगिन करें'}), 401

    data = request.get_json(silent=True) or {}
    result = sync_journey(
        user['user_id'],
        int(data.get('journey_position', 0)),
        int(data.get('journey_streak', 0)),
        data.get('journey_last_date'),
    )
    status = result.pop('status', 200)
    return jsonify(result), status


@bp.route('/api/auth/logout', methods=['POST'])
def api_logout():
    token = _get_token()
    if token:
        logout(token)
    resp = make_response(jsonify({'success': True}))
    resp.delete_cookie('gita_token', path='/')
    return resp
