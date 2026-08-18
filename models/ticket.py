from typing import Literal
from pydantic import Field
from models.base import MongoBaseModel

class Ticket(MongoBaseModel):
    machineId: str = Field(...)
    actionType: Literal['maintenance_ticket', 'inventory_alert'] = Field(...)
    priority: Literal['low', 'medium', 'high'] = Field(...)
    reasoning: str = Field(...)
    status: str = Field(default='open')
