
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(150),nullable=False)
    email: Mapped[str] = mapped_column(String(150),unique=True,nullable=False)
    password: Mapped[str] = mapped_column(String(255),nullable=False,default="not-set")
    role: Mapped[str] = mapped_column(String(30),nullable=False,default="student")
    created_at: Mapped[datetime] = mapped_column(DateTime,server_default=func.now())
