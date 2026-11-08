import os
import uuid
import aiofiles
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.database import get_db
from app.config import settings
from app.models.prescription import Prescription
from app.models.medicine import Medicine
from app.models.user import User
from app.schemas.prescription import PrescriptionOut
from app.security.auth_bearer import get_current_user

router = APIRouter(prefix="/api/prescriptions", tags=["Prescriptions"])

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".pdf"}

@router.post("/upload", response_model=PrescriptionOut, status_code=status.HTTP_201_CREATED)
async def upload_prescription(
    file: UploadFile = File(...),
    doctor_name: Optional[str] = Form(None),
    hospital_clinic: Optional[str] = Form(None),
    prescription_date: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    medicine_id: Optional[int] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify medicine belongs to user if provided
    med_name = None
    if medicine_id:
        med = db.query(Medicine).filter(
            Medicine.id == medicine_id,
            Medicine.user_id == current_user.id
        ).first()
        if not med:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Medicine not found or access denied."
            )
        med_name = med.name

    # Validate file extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Ensure upload directory exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    # Generate unique filename
    safe_name = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, safe_name)

    # Save file
    try:
        async with aiofiles.open(file_path, "wb") as buffer:
            while content := await file.read(1024 * 1024): # 1MB chunks
                await buffer.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )

    # Parse date if provided
    p_date = None
    if prescription_date:
        try:
            p_date = date.fromisoformat(prescription_date)
        except Exception:
            pass

    # Save prescription in DB
    prescription = Prescription(
        user_id=current_user.id,
        medicine_id=medicine_id,
        doctor_name=doctor_name.strip() if doctor_name else None,
        hospital_clinic=hospital_clinic.strip() if hospital_clinic else None,
        prescription_date=p_date,
        file_path=f"/uploads/{safe_name}",
        file_name=file.filename,
        file_type=ext.replace(".", "").upper(),
        notes=notes.strip() if notes else None
    )
    db.add(prescription)
    db.commit()
    db.refresh(prescription)

    return PrescriptionOut(
        id=prescription.id,
        user_id=prescription.user_id,
        medicine_id=prescription.medicine_id,
        medicine_name=med_name,
        doctor_name=prescription.doctor_name,
        hospital_clinic=prescription.hospital_clinic,
        prescription_date=prescription.prescription_date,
        file_path=prescription.file_path,
        file_name=prescription.file_name,
        file_type=prescription.file_type,
        notes=prescription.notes,
        created_at=prescription.created_at
    )

@router.get("", response_model=List[PrescriptionOut])
def list_prescriptions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    prescriptions = (
        db.query(Prescription)
        .filter(Prescription.user_id == current_user.id)
        .order_by(Prescription.created_at.desc())
        .all()
    )
    
    out = []
    for p in prescriptions:
        med = db.query(Medicine).filter(Medicine.id == p.medicine_id).first() if p.medicine_id else None
        out.append(PrescriptionOut(
            id=p.id,
            user_id=p.user_id,
            medicine_id=p.medicine_id,
            medicine_name=med.name if med else None,
            doctor_name=p.doctor_name,
            hospital_clinic=p.hospital_clinic,
            prescription_date=p.prescription_date,
            file_path=p.file_path,
            file_name=p.file_name,
            file_type=p.file_type,
            notes=p.notes,
            created_at=p.created_at
        ))
    return out

@router.delete("/{prescription_id}")
def delete_prescription(
    prescription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    prescription = db.query(Prescription).filter(
        Prescription.id == prescription_id,
        Prescription.user_id == current_user.id
    ).first()
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found or access denied."
        )

    # Delete physical file if exists
    try:
        base_name = os.path.basename(prescription.file_path)
        disk_path = os.path.join(settings.UPLOAD_DIR, base_name)
        if os.path.exists(disk_path):
            os.remove(disk_path)
    except Exception:
        pass

    db.delete(prescription)
    db.commit()
    return {"message": "Prescription deleted successfully."}
