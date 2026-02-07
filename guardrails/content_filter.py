"""Content filtering - profanity, manipulation, off-topic."""

from config import BLOCKED_WORDS, MANIPULATION_PATTERNS, OFFTOPIC_KEYWORDS


def check_content(message: str) -> tuple[bool, str]:
    """
    Check message content for abuse/manipulation.
    Returns (is_ok, reason) - reason: 'profanity' | 'manipulation' | 'offtopic' | ''
    """
    msg_lower = message.lower()

    for word in BLOCKED_WORDS:
        if word in msg_lower:
            return False, 'profanity'

    for pattern in MANIPULATION_PATTERNS:
        if pattern in msg_lower:
            return False, 'manipulation'

    for keyword in OFFTOPIC_KEYWORDS:
        if keyword in msg_lower:
            return False, 'offtopic'

    return True, ''
