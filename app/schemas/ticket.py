from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

TicketStatus = Literal["Новая", "В процессе", "Решена", "Отклонена"]

class TicketCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=3)
    category_id: int | None = Field(default=None, gt=0)
    location_id: int | None = Field(default=None, gt=0)


class TicketStatusUpdate(BaseModel):
    status: TicketStatus


class TicketRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    status: str
    category_id: int | None
    location_id: int | None
    user_id: int | None
    created_at: datetime
    updated_at: datetime
    category_name: str | None = None
    location_name: str | None = None