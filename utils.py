import secrets
import string
from config import DOMAIN

def generate_auth_code() -> str:
    """Generate 8-character alphanumeric code"""
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))

def create_share_url(auth_code: str) -> str:
    """Create shareable URL for joining session"""
    return f"{DOMAIN}/join/{auth_code}"