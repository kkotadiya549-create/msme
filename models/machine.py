from pydantic import Field
from models.base import MongoBaseModel

class Machine(MongoBaseModel):
    machineId: str = Field(...)
    metric: str = Field(...)
    normalRangeMin: float = Field(...)
    normalRangeMax: float = Field(...)
