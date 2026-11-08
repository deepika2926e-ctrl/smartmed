from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base

class MedicineSchedule(Base):
    __tablename__ = "medicine_schedules"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    medicine_id = Column(Integer, ForeignKey("medicines.id", ondelete="CASCADE"), index=True, nullable=False)
    reminder_time = Column(String(10), nullable=False) # e.g. "08:00", "14:00", "20:00"
    time_of_day = Column(String(30), default="morning") # morning, afternoon, evening, night, custom
    days_of_week = Column(String(100), default="Mon,Tue,Wed,Thu,Fri,Sat,Sun")
    dosage_quantity = Column(String(50), default="1 tablet")
    is_active = Column(Boolean, default=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="schedules")
    medicine = relationship("Medicine", back_populates="schedules")
    logs = relationship("MedicineLog", back_populates="schedule")
