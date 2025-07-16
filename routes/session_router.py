from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from models import HostSessionRequest, GenerateCodeResponse, EnterRoomRequest, JoinSessionRequest, SoloSessionRequest, VoiceMessageRequest, SoloVoiceRequest
from utils import generate_auth_code, create_share_url
from config import DOMAIN
import logging

# -- All endpoints removed except non-session/messaging routes, as part of modular split. --
# Session/host/join/leave/status routes will be migrated to 'routes/session.py'.
# Messaging and utility routes will be migrated in subsequent steps.

router = APIRouter()

# === Host session creation ===
@router.post("/api/host/create")
async def create_host_session(req: HostSessionRequest, request: Request):
    pool = request.app.state.db_pool
    async with pool.acquire() as conn:
        result = await conn.fetchrow("""
            INSERT INTO users (user_name, lang, is_host)
            VALUES ($1, $2, TRUE)
            RETURNING id
        """, req.host_name, req.lang)
        host_id = result["id"]
        access_code = generate_auth_code(6)
        channel_result = await conn.fetchrow("""
            INSERT INTO channels (auth_code, host_id, lang, state)
            VALUES ($1, $2, $3, 'waiting')
            RETURNING id
        """, access_code, host_id, req.lang)
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

# === Access code generation ===
@router.post("/api/session/access-code", response_model=GenerateCodeResponse)
async def generate_access_code(request: Request):
    code = generate_auth_code(6)
    url = create_share_url(code)
    return GenerateCodeResponse(auth_code=code, share_url=url)

# === Join existing session ===
@router.post("/api/session/join")
async def join_session(request: JoinSessionRequest):
    pool = request.app.state.db_pool
    async with pool.acquire() as conn:
        channel = await conn.fetchrow("SELECT id, lang, state FROM channels WHERE auth_code=$1", request.auth_code)
        if not channel:
            raise HTTPException(status_code=404, detail="Session not found")
        participant_result = await conn.fetchrow(
            """
            INSERT INTO users (user_name, lang, is_host) VALUES ($1, $2, FALSE) RETURNING id
            """, request.user_name, request.lang,
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

# === Start solo session ===
@router.post("/api/session/solo")
async def start_solo_session(request: SoloSessionRequest):
    import uuid
    return {"solo_session_id": str(uuid.uuid4()), "user_name": request.user_name, "lang": request.lang}

# === Send voice message to group session ===
@router.post("/api/message/send")
async def send_message(request: VoiceMessageRequest, background_tasks: BackgroundTasks):
    import httpx
    pool = request.app.state.db_pool
    payload = request.dict()
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post("http://localhost:3001/pipeline", json=payload)
        resp.raise_for_status()
        # Optionally deliver result to Ably using ably_service or emit event here
    return {"status": "message_sent", "pipeline_result": resp.json()}

# === Send voice message in solo mode ===
@router.post("/api/message/solo")
async def send_solo_message(request: SoloVoiceRequest, background_tasks: BackgroundTasks):
    import httpx
    payload = request.dict()
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post("http://localhost:3001/pipeline", json=payload)
        resp.raise_for_status()
    return {"status": "message_processed", "pipeline_result": resp.json()}

# === Session status/check ===
@router.get("/api/session/{auth_code}/status")
async def get_session_status(auth_code: str):
    pool = request.app.state.db_pool
    async with pool.acquire() as conn:
        channel = await conn.fetchrow("SELECT state, lang FROM channels WHERE auth_code=$1", auth_code)
        if not channel:
            raise HTTPException(status_code=404, detail="Session not found")
        participants = await conn.fetch("SELECT user_id FROM participants p JOIN channels c ON p.channel_id=c.id WHERE c.auth_code=$1", auth_code)
        return {
            "state": channel["state"],
            "lang": channel["lang"],
            "participants": [p["user_id"] for p in participants]
        }

# === Leave session (multi) ===
@router.post("/api/session/leave")
async def leave_session(request: Request):
    user_id = (await request.json()).get("user_id")
    pool = request.app.state.db_pool
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM participants WHERE user_id=$1", user_id)
    return {"status": "left"}

# === End solo session ===
@router.post("/api/solo/end")
async def end_solo_session(request: Request):
    # Solo sessions are stateless; just acknowledge end.
    return {"status": "solo_session_ended"}

# === Supported languages ===
@router.get("/api/languages/supported")
async def get_supported_languages():
    import httpx
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get("http://localhost:3001/languages/all")
        resp.raise_for_status()
        return resp.json()

# === Serve session QR code ===
@router.get("/api/qr/{auth_code}")
async def get_session_qr(auth_code: str):
    import qrcode
    from fastapi.responses import StreamingResponse
    from io import BytesIO
    url = create_share_url(auth_code)
    img = qrcode.make(url)
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")

# === Join link redirect (GET) ===
@router.get("/join/{auth_code}")
async def join_redirect(auth_code: str):
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=f"{DOMAIN}/join/{auth_code}")

# === Health check ===
@router.get("/api/health")
async def health_check():
    return {"status": "ok"}