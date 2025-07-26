import hashlib
import hmac
from typing import Dict
from ..config import settings


def verify_telegram_auth(auth_data: Dict[str, str]) -> bool:
    """Verify Telegram Web App authentication data"""
    check_hash = auth_data.get('hash', '')

    # Create data check string
    data_check_arr = []
    for key in sorted(auth_data.keys()):
        if key != 'hash':
            data_check_arr.append(f"{key}={auth_data[key]}")

    data_check_string = '\n'.join(data_check_arr)

    # Calculate hash
    secret_key = hmac.new(
        b"WebAppData",
        settings.telegram_bot_token.encode(),
        hashlib.sha256
    ).digest()

    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()

    return calculated_hash == check_hash


def is_admin_user(telegram_id: int) -> bool:
    """Check if user is admin based on telegram ID"""
    allowed_ids = settings.parse_allowed_ids()
    return telegram_id in allowed_ids