from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime, timedelta  # Добавьте timedelta здесь!
from ..models.history import HistoryLog


class HistoryService:
    @staticmethod
    def log_action(
            db: Session,
            user_id: int,
            entity_type: str,
            entity_id: int,
            action: str,
            changes: Optional[Dict[str, Any]] = None,
            description: Optional[str] = None
    ):
        """Log an action to history"""
        history = HistoryLog(
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            changes=changes,
            description=description
        )
        db.add(history)
        db.commit()

    @staticmethod
    def get_entity_history(
            db: Session,
            entity_type: str,
            entity_id: int,
            limit: int = 50
    ):
        """Get history for a specific entity"""
        return db.query(HistoryLog).filter(
            HistoryLog.entity_type == entity_type,
            HistoryLog.entity_id == entity_id
        ).order_by(HistoryLog.created_at.desc()).limit(limit).all()

    @staticmethod
    def get_user_history(
            db: Session,
            user_id: int,
            limit: int = 50
    ):
        """Get history of actions by a user"""
        return db.query(HistoryLog).filter(
            HistoryLog.user_id == user_id
        ).order_by(HistoryLog.created_at.desc()).limit(limit).all()

    @staticmethod
    def get_recent_history(
            db: Session,
            hours: int = 24,
            limit: int = 100
    ):
        """Get recent history"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return db.query(HistoryLog).filter(
            HistoryLog.created_at >= cutoff
        ).order_by(HistoryLog.created_at.desc()).limit(limit).all()
