from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserSettingsUpdate(BaseModel):
    email_notifications: Optional[bool] = None
    browser_notifications: Optional[bool] = None
    sound_alerts: Optional[bool] = None
    reminder_advance_minutes: Optional[int] = None
    theme: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None

class UserSettingsOut(BaseModel):
    id: int
    user_id: int
    email_notifications: bool
    browser_notifications: bool
    sound_alerts: bool
    reminder_advance_minutes: int
    theme: str
    timezone: str
    language: str
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
