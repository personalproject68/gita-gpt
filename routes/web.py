"""Web routes - PWA serving."""

from flask import Blueprint, send_from_directory
from config import BASE_DIR

bp = Blueprint('web', __name__)

STATIC_DIR = BASE_DIR / 'static'


@bp.route('/')
def home():
    return send_from_directory(STATIC_DIR, 'index.html')
