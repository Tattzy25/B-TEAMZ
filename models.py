from pydantic import BaseModel, Field
from typing import Optional, Union
from enum import Enum

class HostSessionRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=255)
    display_name: str = Field(..., min_length=1, max_length=100)
    preferred_source_language: str = Field(default="en", max_length=10)
    preferred_target_language: str = Field(default="en", max_length=10)

class GenerateCodeResponse(BaseModel):
    auth_code: str
    channel_name: str
    expires_in_minutes: int
    share_url: str
    qr_code_url: Optional[str] = None

class EnterRoomRequest(BaseModel):
    channel_name: str
    user_id: str

class JoinSessionRequest(BaseModel):
    auth_code: str = Field(..., min_length=8, max_length=8)
    user_id: str = Field(..., min_length=1, max_length=255)
    display_name: str = Field(..., min_length=1, max_length=100)
    preferred_source_language: str = Field(default="en", max_length=10)
    preferred_target_language: str = Field(default="en", max_length=10)

class SoloSessionRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=255)
    display_name: str = Field(..., min_length=1, max_length=100)
    source_language: str = Field(..., max_length=10)
    target_language: str = Field(..., max_length=10)

class VoiceMessageRequest(BaseModel):
    channel_name: str
    user_id: str
    voice_id: str
    audio_data: str  # base64 encoded audio
    duration_seconds: Optional[float] = None

class SoloVoiceRequest(BaseModel):
    session_id: str
    user_id: str
    audio_data: str  # base64 encoded audio
    voice_id: Optional[str] = None

class MessageType(str, Enum):
    text = "text"
    image = "image"
    video = "video"

class MediaMessageRequest(BaseModel):
    channel_name: str
    user_id: str
    message_type: MessageType
    text: Optional[str] = None
    media_url: Optional[str] = None
    media_filename: Optional[str] = None
    media_mimetype: Optional[str] = None
    # Additional flags for permissions (for premium, allow_media_translation, etc.)
    allow_media_translation: Optional[bool] = False