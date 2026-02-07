"""Input sanitization."""


def sanitize_input(message: str) -> str:
    """Sanitize user input - limit length, strip whitespace."""
    message = message[:500]
    message = ' '.join(message.split())
    return message


def is_valid_input(message: str) -> bool:
    """Check if input is valid (not empty/single char)."""
    return bool(message) and len(message.strip()) >= 2
