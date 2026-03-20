import uuid
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.core.config import settings

if TYPE_CHECKING:
    from app.models.auth_user import UserAuth

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    token: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("usersAuth.id"), nullable=False)
    family_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4) 
    expires_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc) + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES))
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)
                                                                                            
    user: Mapped["UserAuth"] = relationship("UserAuth", back_populates="refresh_tokens")
