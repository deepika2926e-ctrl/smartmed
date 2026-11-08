from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    phone = Column(String(30), nullable=True)
    emergency_contact = Column(String(150), nullable=True)
    avatar_url = Column(String(255), nullable=True)
    role = Column(String(20), default="patient")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    medicines = relationship("Medicine", back_populates="user", cascade="all, delete-orphan")
    schedules = relationship("MedicineSchedule", back_populates="user", cascade="all, delete-orphan")
    logs = relationship("MedicineLog", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    prescriptions = relationship("Prescription", back_populates="user", cascade="all, delete-orphan")
    settings = relationship("UserSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")
