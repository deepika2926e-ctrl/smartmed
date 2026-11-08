from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.settings import UserSettings
from app.models.user import User
from app.schemas.settings import UserSettingsOut, UserSettingsUpdate
from app.security.auth_bearer import get_current_user

router = APIRouter(prefix="/api/settings", tags=["User Settings"])

@router.get("", response_model=UserSettingsOut)
def get_user_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    if not settings:
        settings = UserSettings(user_id=current_user.id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings

@router.put("", response_model=UserSettingsOut)
def update_user_settings(
    update_data: UserSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    if not settings:
        settings = UserSettings(user_id=current_user.id)
        db.add(settings)

    update_dict = update_data.dict(exclude_unset=True)
    for field, val in update_dict.items():
        setattr(settings, field, val)

    db.commit()
    db.refresh(settings)
    return settings
