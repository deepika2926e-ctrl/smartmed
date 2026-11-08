from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.medicine import Medicine
from app.models.user import User
from app.schemas.medicine import MedicineCreate, MedicineUpdate, MedicineOut
from app.security.auth_bearer import get_current_user

router = APIRouter(prefix="/api/medicines", tags=["Medicines"])

@router.get("", response_model=List[MedicineOut])
def list_medicines(
    status: Optional[str] = Query(None, description="Filter by status: active, completed, paused"),
    search: Optional[str] = Query(None, description="Search by name or generic name"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Medicine).filter(Medicine.user_id == current_user.id)
    if status:
        query = query.filter(Medicine.status == status)
    if search:
        search_fmt = f"%{search.strip()}%"
        query = query.filter(
            (Medicine.name.ilike(search_fmt)) |
            (Medicine.generic_name.ilike(search_fmt)) |
            (Medicine.category.ilike(search_fmt))
        )
    return query.order_by(Medicine.created_at.desc()).all()

@router.post("", response_model=MedicineOut, status_code=status.HTTP_201_CREATED)
def create_medicine(
    medicine_in: MedicineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_med = Medicine(
        user_id=current_user.id,
        name=medicine_in.name.strip(),
        generic_name=medicine_in.generic_name.strip() if medicine_in.generic_name else None,
        category=medicine_in.category.strip() if medicine_in.category else "General",
        dosage=medicine_in.dosage.strip(),
        form=medicine_in.form,
        frequency=medicine_in.frequency,
        instructions=medicine_in.instructions.strip() if medicine_in.instructions else None,
        start_date=medicine_in.start_date,
        end_date=medicine_in.end_date,
        doctor_name=medicine_in.doctor_name.strip() if medicine_in.doctor_name else None,
        notes=medicine_in.notes.strip() if medicine_in.notes else None,
        status=medicine_in.status
    )
    db.add(new_med)
    db.commit()
    db.refresh(new_med)
    return new_med

@router.get("/{medicine_id}", response_model=MedicineOut)
def get_medicine(
    medicine_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    med = db.query(Medicine).filter(
        Medicine.id == medicine_id,
        Medicine.user_id == current_user.id
    ).first()
    if not med:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicine not found or access denied."
        )
    return med

@router.put("/{medicine_id}", response_model=MedicineOut)
def update_medicine(
    medicine_id: int,
    med_update: MedicineUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    med = db.query(Medicine).filter(
        Medicine.id == medicine_id,
        Medicine.user_id == current_user.id
    ).first()
    if not med:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicine not found or access denied."
        )

    update_dict = med_update.dict(exclude_unset=True)
    for field, val in update_dict.items():
        if val is not None and isinstance(val, str):
            val = val.strip()
        setattr(med, field, val)

    db.commit()
    db.refresh(med)
    return med

@router.delete("/{medicine_id}", status_code=status.HTTP_200_OK)
def delete_medicine(
    medicine_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    med = db.query(Medicine).filter(
        Medicine.id == medicine_id,
        Medicine.user_id == current_user.id
    ).first()
    if not med:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicine not found or access denied."
        )

    db.delete(med)
    db.commit()
    return {"message": f"Medicine '{med.name}' deleted successfully."}
