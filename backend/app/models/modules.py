from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func

from app.db.base import Base


class Modules(Base):
    __tablename__ = "modules"

    module_id = Column(Integer, primary_key=True, index=True)
    priority = Column(Integer, nullable=False, default=100, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
