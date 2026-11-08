from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base

class MedicineLog(Base):
    __tablename__ = "medicine_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    medicine_id = Column(Integer, ForeignKey("medicines.id", ondelete="CASCADE"), index=True, nullable=False)
    schedule_id = Column(Integer, ForeignKey("medicine_schedules.id", ondelete="SET NULL"), nullable=True)
    scheduled_time = Column(DateTime, nullable=False, index=True)
    logged_time = Column(DateTime, nullable=True)
    status = Column(String(20), default="pending", index=True) # pending, taken, skipped, missed
    notes = Column(Text, nullable=True)
    snooze_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="logs")
    medicine = relationship("Medicine", back_populates="logs")
    schedule = relationship("MedicineSchedule", back_populates="logs")
