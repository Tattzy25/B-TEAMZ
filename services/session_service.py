from services.ably_service import create_ably_token
from utils import generate_auth_code, create_share_url
import uuid

async def create_host_session(conn, host_name, lang):
    result = await conn.fetchrow("""
        INSERT INTO users (user_name, lang, is_host)
        VALUES ($1, $2, TRUE)
        RETURNING id
    """, host_name, lang)
    host_id = result["id"]
    access_code = generate_auth_code(6)
    channel_result = await conn.fetchrow("""
        INSERT INTO channels (auth_code, host_id, lang, state)
        VALUES ($1, $2, $3, 'waiting')
        RETURNING id
    """, access_code, host_id, lang)
    channel_id = channel_result["id"]
    await conn.execute("""
        INSERT INTO participants (user_id, channel_id, joined_at)
        VALUES ($1, $2, NOW())
    """, host_id, channel_id)
    ably_token = create_ably_token(client_id=f"host-{host_id}")
    return {
        "auth_code": access_code,
        "host_id": host_id,
        "ably_token": ably_token,
        "channel_id": channel_id,
        "share_url": create_share_url(access_code),
    }

async def generate_access_code():
    code = generate_auth_code(6)
    url = create_share_url(code)
    return {"auth_code": code, "share_url": url}

async def join_session(conn, user_name, lang, auth_code):
    channel = await conn.fetchrow("SELECT id, lang, state FROM channels WHERE auth_code=$1", auth_code)
    if not channel:
        return None
    participant_result = await conn.fetchrow(
        """
        INSERT INTO users (user_name, lang, is_host) VALUES ($1, $2, FALSE) RETURNING id
        """, user_name, lang,
    )
    user_id = participant_result["id"]
    await conn.execute("INSERT INTO participants (user_id, channel_id, joined_at) VALUES ($1, $2, NOW())", user_id, channel["id"])
    ably_token = create_ably_token(client_id=f"user-{user_id}")
    return {
        "ably_token": ably_token,
        "user_id": user_id,
        "channel_id": channel["id"],
        "host_lang": channel["lang"],
        "channel_state": channel["state"]
    }

async def start_solo_session(user_name, lang):
    return {"solo_session_id": str(uuid.uuid4()), "user_name": user_name, "lang": lang}

async def get_session_status(conn, auth_code):
    channel = await conn.fetchrow("SELECT state, lang FROM channels WHERE auth_code=$1", auth_code)
    if not channel:
        return None
    participants = await conn.fetch("SELECT user_id FROM participants p JOIN channels c ON p.channel_id=c.id WHERE c.auth_code=$1", auth_code)
    return {
        "state": channel["state"],
        "lang": channel["lang"],
        "participants": [p["user_id"] for p in participants]
    }

async def leave_session(conn, user_id):
    await conn.execute("DELETE FROM participants WHERE user_id=$1", user_id)
    return {"status": "left"}

async def end_solo_session():
    return {"status": "solo_session_ended"}