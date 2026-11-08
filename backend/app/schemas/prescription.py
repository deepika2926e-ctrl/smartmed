from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class PrescriptionCreate(BaseModel):
    medicine_id: Optional[int] = None
    doctor_name: Optional[str] = None
    hospital_clinic: Optional[str] = None
    prescription_date: Optional[date] = None
    notes: Optional[str] = None

class PrescriptionOut(BaseModel):
    id: int
    user_id: int
    medicine_id: Optional[int] = None
    medicine_name: Optional[str] = None
    doctor_name: Optional[str] = None
    hospital_clinic: Optional[str] = None
    prescription_date: Optional[date] = None
    file_path: str
    file_name: str
    file_type: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
