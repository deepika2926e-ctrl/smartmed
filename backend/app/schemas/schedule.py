from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime

class ScheduleBase(BaseModel):
    medicine_id: int
    reminder_time: str = Field(..., pattern=r"^\d{2}:\d{2}$") # e.g. "08:00"
    time_of_day: str = "morning" # morning, afternoon, evening, night, custom
    days_of_week: str = "Mon,Tue,Wed,Thu,Fri,Sat,Sun"
    dosage_quantity: str = "1 tablet"
    is_active: bool = True
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class ScheduleCreate(ScheduleBase):
    pass

class ScheduleUpdate(BaseModel):
    reminder_time: Optional[str] = None
    time_of_day: Optional[str] = None
    days_of_week: Optional[str] = None
    dosage_quantity: Optional[str] = None
    is_active: Optional[bool] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class ScheduleOut(ScheduleBase):
    id: int
    user_id: int
    medicine_name: Optional[str] = None
    medicine_form: Optional[str] = None
    medicine_dosage: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
