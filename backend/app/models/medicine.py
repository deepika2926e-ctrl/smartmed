from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base

class Medicine(Base):
    __tablename__ = "medicines"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    name = Column(String(150), nullable=False, index=True)
    generic_name = Column(String(150), nullable=True)
    category = Column(String(100), nullable=True, index=True)
    dosage = Column(String(100), nullable=False)  # e.g., "500 mg", "10 ml"
    form = Column(String(50), default="Tablet")    # Tablet, Capsule, Syrup, Injection, etc.
    frequency = Column(String(100), default="Once daily")
    instructions = Column(String(255), nullable=True) # e.g. "Take with food"
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    doctor_name = Column(String(150), nullable=True)
    notes = Column(Text, nullable=True)
    status = Column(String(20), default="active", index=True) # active, completed, paused
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="medicines")
    schedules = relationship("MedicineSchedule", back_populates="medicine", cascade="all, delete-orphan")
    logs = relationship("MedicineLog", back_populates="medicine", cascade="all, delete-orphan")
    prescriptions = relationship("Prescription", back_populates="medicine")
