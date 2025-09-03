from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.user import User, UserRole
from ..utils.dependencies import get_current_user, require_super_admin

router = APIRouter()


@router.get("/", response_model=List[dict])
async def get_all_users(
        db: Session = Depends(get_db),
        current_user: User = Depends(require_super_admin)
):
    """Получить список всех пользователей (только для Super Admin)"""
    users = db.query(User).all()

    result = []
    for user in users:
        result.append({
            "id": user.id,
            "telegram_id": user.telegram_id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "email": user.email,
            "phone": user.phone,
            "role": user.role.value,
            "is_active": user.is_active,
            "is_admin": user.is_admin,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "can_create_bookings": user.can_create_bookings,
            "can_edit_bookings": user.can_edit_bookings,
            "can_delete_any_booking": user.can_delete_any_booking,
            "can_view_analytics": user.can_view_analytics,
            "can_manage_settings": user.can_manage_settings,
            "can_manage_users": user.can_manage_users
        })

    return result


@router.patch("/{user_id}/role")
async def update_user_role(
        user_id: int,
        role_data: dict,
        db: Session = Depends(get_db),
        current_user: User = Depends(require_super_admin)
):
    """Изменить роль пользователя (только для Super Admin)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Нельзя изменить роль себе
    if user.id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Cannot change your own role"
        )

    try:
        new_role = role_data.get("role", "").upper()
        if new_role not in [r.name for r in UserRole]:
            # Пробуем найти роль по значению
            for role in UserRole:
                if role.value == role_data.get("role", "").lower():
                    new_role = role.name
                    break

        user.role = UserRole[new_role]

        # Обновляем флаг is_admin для обратной совместимости
        user.is_admin = user.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]

        db.commit()

        return {
            "message": "Role updated successfully",
            "user_id": user.id,
            "new_role": user.role.value
        }
    except KeyError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role. Must be one of: {', '.join([r.value for r in UserRole])}"
        )


@router.patch("/{user_id}/status")
async def update_user_status(
        user_id: int,
        status_data: dict,
        db: Session = Depends(get_db),
        current_user: User = Depends(require_super_admin)
):
    """Активировать/деактивировать пользователя (только для Super Admin)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Нельзя деактивировать себя
    if user.id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Cannot deactivate your own account"
        )

    user.is_active = status_data.get("is_active", user.is_active)
    db.commit()

    return {
        "message": "Status updated successfully",
        "user_id": user.id,
        "is_active": user.is_active
    }


@router.get("/me", response_model=dict)
async def get_current_user_info(
        current_user: User = Depends(get_current_user)
):
    """Получить информацию о текущем пользователе"""
    return {
        "id": current_user.id,
        "telegram_id": current_user.telegram_id,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "username": current_user.username,
        "email": current_user.email,
        "phone": current_user.phone,
        "role": current_user.role.value,
        "role_display": current_user.get_role_display(),
        "is_active": current_user.is_active,
        "is_admin": current_user.is_admin,
        "permissions": {
            "can_view_rooms": current_user.can_view_rooms,
            "can_create_bookings": current_user.can_create_bookings,
            "can_edit_bookings": current_user.can_edit_bookings,
            "can_delete_bookings": current_user.can_delete_bookings,
            "can_delete_any_booking": current_user.can_delete_any_booking,
            "can_view_analytics": current_user.can_view_analytics,
            "can_export_data": current_user.can_export_data,
            "can_manage_settings": current_user.can_manage_settings,
            "can_manage_users": current_user.can_manage_users,
            "can_view_history": current_user.can_view_history
        },
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None
    }


@router.patch("/me")
async def update_current_user(
        user_data: dict,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Обновить свои данные"""
    # Пользователь может обновить только свои контактные данные
    if "first_name" in user_data:
        current_user.first_name = user_data["first_name"]
    if "last_name" in user_data:
        current_user.last_name = user_data["last_name"]
    if "email" in user_data:
        current_user.email = user_data["email"]
    if "phone" in user_data:
        current_user.phone = user_data["phone"]

    db.commit()

    return {
        "message": "Profile updated successfully",
        "user": {
            "id": current_user.id,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "email": current_user.email,
            "phone": current_user.phone
        }
    }