from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.medicine_info import EducationalMedicine
from app.schemas.medicine_info import EducationalMedicineOut, EducationalMedicineSummary

router = APIRouter(prefix="/api/medicine-info", tags=["Educational Medicine Information"])

@router.get("", response_model=List[EducationalMedicineSummary])
def search_educational_medicines(
    search: Optional[str] = Query(None, description="Search term across name, generic name, uses"),
    category: Optional[str] = Query(None, description="Filter by category"),
    db: Session = Depends(get_db)
):
    query = db.query(EducationalMedicine)
    if category and category.lower() != "all":
        query = query.filter(EducationalMedicine.category.ilike(f"%{category.strip()}%"))
    if search:
        search_fmt = f"%{search.strip()}%"
        query = query.filter(
            (EducationalMedicine.name.ilike(search_fmt)) |
            (EducationalMedicine.generic_name.ilike(search_fmt)) |
            (EducationalMedicine.brand_names.ilike(search_fmt)) |
            (EducationalMedicine.common_uses.ilike(search_fmt)) |
            (EducationalMedicine.category.ilike(search_fmt))
        )
    return query.order_by(EducationalMedicine.name.asc()).all()

@router.get("/categories", response_model=List[str])
def get_categories(db: Session = Depends(get_db)):
    rows = db.query(EducationalMedicine.category).distinct().all()
    categories = sorted(list({r[0] for r in rows if r[0]}))
    return categories

@router.get("/{med_id}", response_model=EducationalMedicineOut)
def get_educational_medicine_details(med_id: int, db: Session = Depends(get_db)):
    med = db.query(EducationalMedicine).filter(EducationalMedicine.id == med_id).first()
    if not med:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Educational medicine entry not found."
        )
    return med

@router.get("/{med_id}/related", response_model=List[EducationalMedicineSummary])
def get_related_medicines(med_id: int, db: Session = Depends(get_db)):
    med = db.query(EducationalMedicine).filter(EducationalMedicine.id == med_id).first()
    if not med:
        return []
    
    related = (
        db.query(EducationalMedicine)
        .filter(
            EducationalMedicine.category == med.category,
            EducationalMedicine.id != med.id
        )
        .limit(4)
        .all()
    )
    return related
