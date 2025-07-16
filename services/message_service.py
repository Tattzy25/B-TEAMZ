import httpx
import os
from fastapi import UploadFile
from uuid import uuid4
from typing import Optional

MEDIA_DIR = "media_uploads"
os.makedirs(MEDIA_DIR, exist_ok=True)

async def save_media_file(file: UploadFile) -> str:
    ext = os.path.splitext(file.filename)[1]
    unique_name = f"{uuid4().hex}{ext}"
    out_path = os.path.join(MEDIA_DIR, unique_name)
    with open(out_path, "wb") as out:
        content = await file.read()
        out.write(content)
    return f"/{MEDIA_DIR}/{unique_name}"

async def process_message(payload: dict, file: Optional[UploadFile] = None):
    if payload.get("message_type") == "text":
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post("http://localhost:3001/pipeline", json=payload)
            resp.raise_for_status()
            return resp.json()
    elif payload.get("message_type") in ("image", "video") and file:
        url = await save_media_file(file)
        media_payload = {
            **payload,
            "media_url": url,
            "media_filename": file.filename,
            "media_mimetype": file.content_type,
        }
        # No pipeline processing for media, just return Ably/broadcast-compatible ref
        # (Route this payload to Ably pub if required, or return for further handling)
        return {"status": "media_saved", "media": media_payload}
    else:
        return {"error": "Invalid message type or missing file."}