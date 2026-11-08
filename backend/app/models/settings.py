from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base

class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    email_notifications = Column(Boolean, default=True)
    browser_notifications = Column(Boolean, default=True)
    sound_alerts = Column(Boolean, default=True)
    reminder_advance_minutes = Column(Integer, default=0)
    theme = Column(String(20), default="light") # light, dark
    timezone = Column(String(50), default="UTC")
    language = Column(String(20), default="en")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="settings")
