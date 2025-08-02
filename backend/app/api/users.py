from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.user import User, UserRole
from ..schemas.user import UserResponse, UserUpdate
from ..utils.dependencies import get_current_user

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
async def get_users(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Get all users (only for admins)"""
    if not current_user.can_manage_bookings:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view users"
        )

    users = db.query(User).order_by(User.created_at.desc()).all()
    return users


@router.get("/admins", response_model=List[UserResponse])
async def get_admins(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Get all admin users"""
    if not current_user.can_manage_bookings:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view admin list"
        )

    admins = db.query(User).filter(
        User.role.in_([UserRole.ADMIN, UserRole.SUPER_ADMIN])
    ).order_by(User.created_at.desc()).all()
    return admins


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
        user_id: int,
        user_update: UserUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Update user (only for super admins)"""
    if not current_user.can_manage_users:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admins can update users"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Нельзя понизить права супер-админа самому себе
    if user.id == current_user.id and user_update.role and user_update.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot downgrade your own super admin role"
        )

    # Обновляем поля
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    # Синхронизируем is_admin с role
    if user.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        user.is_admin = True
    else:
        user.is_admin = False

    db.commit()
    db.refresh(user)
    return user


@router.post("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Deactivate user (only for super admins)"""
    if not current_user.can_manage_users:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admins can deactivate users"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Нельзя деактивировать себя
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate yourself"
        )

    user.is_active = False
    db.commit()
    db.refresh(user)
    return user


@router.post("/{user_id}/activate", response_model=UserResponse)
async def activate_user(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Activate user (only for super admins)"""
    if not current_user.can_manage_users:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admins can activate users"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.is_active = True
    db.commit()
    db.refresh(user)
    return user