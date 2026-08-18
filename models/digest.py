from pydantic import Field
from datetime import datetime
from models.base import MongoBaseModel

class Digest(MongoBaseModel):
    date: str = Field(...)
    content: str = Field(...)
    sentAt: datetime = Field(...)
