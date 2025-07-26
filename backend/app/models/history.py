from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base
from datetime import datetime


class HistoryLog(Base):
    __tablename__ = "history_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    entity_type = Column(String, nullable=False)  # 'room', 'booking', 'user'
    entity_id = Column(Integer, nullable=False)
    action = Column(String, nullable=False)  # 'create', 'update', 'delete'
    changes = Column(JSON, nullable=True)  # Old and new values
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", backref="history_logs")