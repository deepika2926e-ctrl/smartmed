from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base

class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    medicine_id = Column(Integer, ForeignKey("medicines.id", ondelete="SET NULL"), nullable=True)
    doctor_name = Column(String(150), nullable=True)
    hospital_clinic = Column(String(200), nullable=True)
    prescription_date = Column(Date, nullable=True)
    file_path = Column(String(255), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="prescriptions")
    medicine = relationship("Medicine", back_populates="prescriptions")
