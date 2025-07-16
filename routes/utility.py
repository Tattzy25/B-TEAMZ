from fastapi import APIRouter
from services.utility_service import fetch_supported_languages, create_qr_code, build_join_redirect_url, health_check
from fastapi.responses import StreamingResponse, RedirectResponse

router = APIRouter()

@router.get("/api/languages/supported")
async def get_supported_languages():
    return await fetch_supported_languages()

@router.get("/api/qr/{auth_code}")
async def get_session_qr(auth_code: str):
    buf = create_qr_code(auth_code)
    return StreamingResponse(buf, media_type="image/png")

@router.get("/join/{auth_code}")
async def join_redirect(auth_code: str):
    url = build_join_redirect_url(auth_code)
    return RedirectResponse(url=url)

@router.get("/api/health")
async def health_check_endpoint():
    return health_check()