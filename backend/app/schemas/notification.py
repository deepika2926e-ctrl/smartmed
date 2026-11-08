from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NotificationCreate(BaseModel):
    title: str
    message: str
    notification_type: str = "reminder"
    medicine_id: Optional[int] = None
    scheduled_for: Optional[datetime] = None

class NotificationOut(BaseModel):
    id: int
    user_id: int
    medicine_id: Optional[int] = None
    title: str
    message: str
    notification_type: str
    is_read: bool
    scheduled_for: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
