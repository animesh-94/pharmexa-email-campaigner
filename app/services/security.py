import hmac
import hashlib
from app.config import settings

def generate_unsubscribe_token(subscriber_id: str, campaign_id: str) -> str:
    """Generate a secure HMAC token for a given subscriber and campaign."""
    key = settings.SECRET_KEY.encode('utf-8')
    msg = f"{subscriber_id}:{campaign_id}".encode('utf-8')
    return hmac.new(key, msg, hashlib.sha256).hexdigest()

def verify_unsubscribe_token(subscriber_id: str, campaign_id: str, token: str) -> bool:
    """Verify if the provided token is valid."""
    expected_token = generate_unsubscribe_token(subscriber_id, campaign_id)
    return hmac.compare_digest(expected_token, token)
