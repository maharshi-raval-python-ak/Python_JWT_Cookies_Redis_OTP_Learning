from app.core.database import Base
from sqlalchemy import CheckConstraint, String, DateTime, func, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List
from sqlalchemy import Enum as SQLAlchemyEnum

if TYPE_CHECKING:
    from app.models.refresh_token_model import RefreshToken


class Role(str, Enum):
    Public = "Public"
    Editor = "Editor"
    Admin = "Admin"

class UserAuth(Base):
    __tablename__ = "usersAuth"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    hashed_password: Mapped[str] = mapped_column(String)
    roles: Mapped[List[Role]] = mapped_column(
        ARRAY(SQLAlchemyEnum(Role, native_enum=False)),
        CheckConstraint("array_length(roles, 1) > 0", name="roles_not_empty"),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
