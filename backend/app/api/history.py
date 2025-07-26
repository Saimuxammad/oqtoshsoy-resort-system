from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..services.history_service import HistoryService
from ..utils.dependencies import get_current_user

router = APIRouter()

@router.get("/entity/{entity_type}/{entity_id}")
async def get_entity_history(
    entity_type: str,
    entity_id: int,
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get history for a specific entity"""
    history = HistoryService.get_entity_history(db, entity_type, entity_id, limit)
    return history

@router.get("/user/{user_id}")
async def get_user_history(
    user_id: int,
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get history of actions by a user"""
    history = HistoryService.get_user_history(db, user_id, limit)
    return history

@router.get("/recent")
async def get_recent_history(
    hours: int = Query(24, ge=1, le=168),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get recent history"""
    history = HistoryService.get_recent_history(db, hours, limit)
    return history