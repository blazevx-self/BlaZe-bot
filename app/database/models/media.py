from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.models import Base

class MediaOrm(Base):
    __tablename__ = 'media'

    path: Mapped[str] = mapped_column(primary_key=True)
    file_id: Mapped[str] = mapped_column(nullable=False)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())