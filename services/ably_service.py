from fastapi import HTTPException
from ably import AblyRest
import logging
from config import ABLY_API_KEY

logger = logging.getLogger(__name__)

ably = AblyRest(ABLY_API_KEY) if ABLY_API_KEY else None

async def create_ably_token(user_id: str, channel_name: str) -> dict:
    """Create Ably token for real-time communication"""
    if not ably:
        raise HTTPException(status_code=500, detail="Real-time service not available")
    try:
        token_request = ably.auth.create_token_request({
            'client_id': user_id,
            'capability': {channel_name: ['*']},
            'ttl': 7200000
        })
        return token_request
    except Exception as e:
        logger.error(f"Failed to create Ably token: {e}")
        raise HTTPException(status_code=500, detail="Failed to create communication token")