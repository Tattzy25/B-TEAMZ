from fastapi import APIRouter, Request, BackgroundTasks, UploadFile, File, Form
from models import VoiceMessageRequest, SoloVoiceRequest, MessageType
from services.message_service import process_message
from typing import Optional

router = APIRouter()

@router.post("/api/message/send")
async def send_message(
    channel_name: str = Form(...),
    user_id: str = Form(...),
    message_type: MessageType = Form(...),
    text: Optional[str] = Form(None),
    allow_media_translation: Optional[bool] = Form(False),
    file: Optional[UploadFile] = File(None),
    background_tasks: BackgroundTasks = None,
    req: Request = None):
    payload = {
        "channel_name": channel_name,
        "user_id": user_id,
        "message_type": message_type.value if hasattr(message_type, 'value') else message_type,
        "text": text,
        "allow_media_translation": allow_media_translation
    }
    result = await process_message(payload, file)
    return result

@router.post("/api/message/solo")
async def send_solo_message(request: SoloVoiceRequest, background_tasks: BackgroundTasks):
    # Solo messages are audio-only, local, NOT routed to chatroom or media
    payload = request.dict()
    from services.message_service import send_message_to_pipeline
    result = await send_message_to_pipeline(payload)
    return {"status": "message_processed", "pipeline_result": result}