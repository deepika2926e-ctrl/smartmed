from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.settings import UserSettings
from app.schemas.user import UserRegister, UserLogin, UserOut, Token
from app.security.hashing import get_password_hash, verify_password
from app.security.auth_bearer import create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    # Check if email already registered
    existing_user = db.query(User).filter(User.email == user_data.email.lower().strip()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )

    # Hash password securely
    hashed_pwd = get_password_hash(user_data.password)

    new_user = User(
        full_name=user_data.full_name.strip(),
        email=user_data.email.lower().strip(),
        hashed_password=hashed_pwd,
        phone=user_data.phone,
        emergency_contact=user_data.emergency_contact,
        role="patient",
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create default user settings
    user_settings = UserSettings(user_id=new_user.id)
    db.add(user_settings)
    db.commit()

    # Generate token
    token = create_access_token({"sub": str(new_user.id), "email": new_user.email})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": new_user
    }

@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email.lower().strip()).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password."
        )
    
    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated."
        )

    token = create_access_token({"sub": str(user.id), "email": user.email})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
