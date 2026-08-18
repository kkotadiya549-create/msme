from typing import Optional, Literal
from pydantic import Field
from datetime import datetime
from models.base import MongoBaseModel

class Message(MongoBaseModel):
    senderNumber: str = Field(...)
    messageText: Optional[str] = Field(default=None)
    messageType: Literal['text', 'voice', 'image', 'document', 'audio', 'video', 'location', 'contacts', 'interactive', 'button', 'reaction', 'sticker', 'system', 'unknown', 'unsupported'] = Field(default='text')
    timestamp: datetime = Field(...)
    processed: bool = Field(default=False)
