from fastapi import APIRouter, HTTPException, Request
from models import HostSessionRequest, GenerateCodeResponse, JoinSessionRequest, SoloSessionRequest
from services import session_service

router = APIRouter()

@router.post("/api/host/create")
async def create_host_session(req: HostSessionRequest, request: Request):
    pool = request.app.state.db_pool
    async with pool.acquire() as conn:
        return await session_service.create_host_session(conn, req.host_name, req.lang)

@router.post("/api/session/access-code", response_model=GenerateCodeResponse)
async def generate_access_code(request: Request):
    code_obj = await session_service.generate_access_code()
    return GenerateCodeResponse(**code_obj)

@router.post("/api/session/join")
async def join_session(request: JoinSessionRequest):
    pool = request.app.state.db_pool
    async with pool.acquire() as conn:
        result = await session_service.join_session(conn, request.user_name, request.lang, request.auth_code)
        if not result:
            raise HTTPException(status_code=404, detail="Session not found")
        return result

@router.post("/api/session/solo")
async def start_solo_session(request: SoloSessionRequest):
    return await session_service.start_solo_session(request.user_name, request.lang)

@router.get("/api/session/{auth_code}/status")
async def get_session_status(auth_code: str, request: Request):
    pool = request.app.state.db_pool
    async with pool.acquire() as conn:
        result = await session_service.get_session_status(conn, auth_code)
        if not result:
            raise HTTPException(status_code=404, detail="Session not found")
        return result

@router.post("/api/session/leave")
async def leave_session(request: Request):
    user_id = (await request.json()).get("user_id")
    pool = request.app.state.db_pool
    async with pool.acquire() as conn:
        return await session_service.leave_session(conn, user_id)

@router.post("/api/solo/end")
async def end_solo_session(request: Request):
    return await session_service.end_solo_session()