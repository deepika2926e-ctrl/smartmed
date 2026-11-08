from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserOut, UserUpdate, PasswordChange
from app.security.hashing import get_password_hash, verify_password
from app.security.auth_bearer import get_current_user

router = APIRouter(prefix="/api/users", tags=["Users"])

@router.put("/profile", response_model=UserOut)
def update_profile(
    update_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if update_data.full_name is not None:
        current_user.full_name = update_data.full_name.strip()
    if update_data.phone is not None:
        current_user.phone = update_data.phone.strip() if update_data.phone else None
    if update_data.emergency_contact is not None:
        current_user.emergency_contact = update_data.emergency_contact.strip() if update_data.emergency_contact else None
    if update_data.avatar_url is not None:
        current_user.avatar_url = update_data.avatar_url.strip() if update_data.avatar_url else None

    db.commit()
    db.refresh(current_user)
    return current_user

@router.put("/change-password")
def change_password(
    pwd_data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not verify_password(pwd_data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password does not match our records."
        )

    current_user.hashed_password = get_password_hash(pwd_data.new_password)
    db.commit()
    return {"message": "Password changed successfully."}
