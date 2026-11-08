from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime

class MedicineBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    generic_name: Optional[str] = None
    category: Optional[str] = "General"
    dosage: str = Field(..., min_length=1, max_length=100) # e.g. "500 mg"
    form: str = "Tablet" # Tablet, Capsule, Syrup, Injection, Inhaler, Drops, etc.
    frequency: str = "Once daily"
    instructions: Optional[str] = None # e.g. "Take after food"
    start_date: date
    end_date: Optional[date] = None
    doctor_name: Optional[str] = None
    notes: Optional[str] = None
    status: str = "active" # active, completed, paused

class MedicineCreate(MedicineBase):
    pass

class MedicineUpdate(BaseModel):
    name: Optional[str] = None
    generic_name: Optional[str] = None
    category: Optional[str] = None
    dosage: Optional[str] = None
    form: Optional[str] = None
    frequency: Optional[str] = None
    instructions: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    doctor_name: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None

class MedicineOut(MedicineBase):
    id: int
    user_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
