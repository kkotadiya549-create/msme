from pydantic import Field
from datetime import datetime
from models.base import MongoBaseModel

class SensorReading(MongoBaseModel):
    machineId: str = Field(...)
    metric: str = Field(...)
    value: float = Field(...)
    timestamp: datetime = Field(...)
