from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class EducationalMedicineBase(BaseModel):
    name: str
    generic_name: str
    brand_names: Optional[str] = None
    category: str
    description: str
    common_uses: str
    mechanism_of_action: str
    available_forms: str
    common_side_effects: str
    serious_side_effects: str
    precautions: str
    drug_interactions: str
    storage_instructions: str
    general_usage_info: str
    reference_sources: str
    disclaimer: str

class EducationalMedicineOut(EducationalMedicineBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class EducationalMedicineSummary(BaseModel):
    id: int
    name: str
    generic_name: str
    category: str
    common_uses: str
    available_forms: str

    class Config:
        from_attributes = True
