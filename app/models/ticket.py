from datetime import datetime
from typing import Literal

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="Новая")
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"))
    location_id: Mapped[int | None] = mapped_column(ForeignKey("locations.id"))
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"),nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())