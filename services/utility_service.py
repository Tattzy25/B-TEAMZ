import httpx
from utils import create_share_url
from config import DOMAIN
import qrcode
from io import BytesIO

async def fetch_supported_languages():
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get("http://localhost:3001/languages/all")
        resp.raise_for_status()
        return resp.json()

def create_qr_code(auth_code):
    url = create_share_url(auth_code)
    img = qrcode.make(url)
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

def build_join_redirect_url(auth_code):
    return f"{DOMAIN}/join/{auth_code}"

def health_check():
    return {"status": "ok"}