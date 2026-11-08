from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.database import Base

class EducationalMedicine(Base):
    __tablename__ = "educational_medicines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), index=True, nullable=False)
    generic_name = Column(String(150), index=True, nullable=False)
    brand_names = Column(String(255), nullable=True)
    category = Column(String(100), index=True, nullable=False)
    description = Column(Text, nullable=False)
    common_uses = Column(Text, nullable=False)
    mechanism_of_action = Column(Text, nullable=False)
    available_forms = Column(String(255), nullable=False)
    common_side_effects = Column(Text, nullable=False)
    serious_side_effects = Column(Text, nullable=False)
    precautions = Column(Text, nullable=False)
    drug_interactions = Column(Text, nullable=False)
    storage_instructions = Column(Text, nullable=False)
    general_usage_info = Column(Text, nullable=False)
    reference_sources = Column(Text, nullable=False)
    disclaimer = Column(
        Text,
        default=(
            "Educational Information Only: This summary is based on trustworthy references "
            "(MedlinePlus, NHS, FDA/EMA official prescribing labels) and is for general knowledge. "
            "It does not constitute personalized medical advice. Never start, discontinue, or alter any "
            "medication without the express direction of a licensed healthcare provider."
        )
    )
    created_at = Column(DateTime, server_default=func.now())
