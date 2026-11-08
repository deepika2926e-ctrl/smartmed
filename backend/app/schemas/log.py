from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class LogCreate(BaseModel):
    medicine_id: int
    schedule_id: Optional[int] = None
    scheduled_time: datetime
    status: str = "pending" # pending, taken, skipped, missed
    notes: Optional[str] = None

class LogStatusUpdate(BaseModel):
    status: str # taken, skipped, missed, pending
    notes: Optional[str] = None
    logged_time: Optional[datetime] = None

class LogSnooze(BaseModel):
    snooze_minutes: int = 15

class LogOut(BaseModel):
    id: int
    user_id: int
    medicine_id: int
    schedule_id: Optional[int] = None
    scheduled_time: datetime
    logged_time: Optional[datetime] = None
    status: str
    notes: Optional[str] = None
    snooze_until: Optional[datetime] = None
    medicine_name: Optional[str] = None
    medicine_dosage: Optional[str] = None
    medicine_form: Optional[str] = None
    instructions: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
