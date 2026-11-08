from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta, date, time
from app.database import get_db
from app.models.log import MedicineLog
from app.models.medicine import Medicine
from app.models.user import User
from app.schemas.log import LogOut, LogStatusUpdate, LogSnooze, LogCreate
from app.security.auth_bearer import get_current_user
from app.services.reminder_service import create_medicine_notification

router = APIRouter(prefix="/api/logs", tags=["Medicine Logs & Tracking"])

@router.get("", response_model=List[LogOut])
def get_logs(
    status: Optional[str] = Query(None, description="taken, skipped, missed, pending"),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    medicine_id: Optional[int] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = (
        db.query(MedicineLog, Medicine.name, Medicine.dosage, Medicine.form, Medicine.instructions)
        .join(Medicine, Medicine.id == MedicineLog.medicine_id)
        .filter(MedicineLog.user_id == current_user.id)
    )

    if status:
        query = query.filter(MedicineLog.status == status)
    if medicine_id:
        query = query.filter(MedicineLog.medicine_id == medicine_id)
    if date_from:
        dt_from = datetime.combine(date_from, time.min)
        query = query.filter(MedicineLog.scheduled_time >= dt_from)
    if date_to:
        dt_to = datetime.combine(date_to, time.max)
        query = query.filter(MedicineLog.scheduled_time <= dt_to)

    results = query.order_by(MedicineLog.scheduled_time.desc()).limit(limit).all()

    out = []
    for log, med_name, med_dosage, med_form, instructions in results:
        out.append(LogOut(
            id=log.id,
            user_id=log.user_id,
            medicine_id=log.medicine_id,
            schedule_id=log.schedule_id,
            scheduled_time=log.scheduled_time,
            logged_time=log.logged_time,
            status=log.status,
            notes=log.notes,
            snooze_until=log.snooze_until,
            medicine_name=med_name,
            medicine_dosage=med_dosage,
            medicine_form=med_form,
            instructions=instructions,
            created_at=log.created_at
        ))
    return out

@router.put("/{log_id}/status", response_model=LogOut)
def update_log_status(
    log_id: int,
    status_update: LogStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    log = db.query(MedicineLog).filter(
        MedicineLog.id == log_id,
        MedicineLog.user_id == current_user.id
    ).first()
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dose log not found or access denied."
        )

    log.status = status_update.status
    log.logged_time = status_update.logged_time or datetime.now()
    if status_update.notes:
        log.notes = status_update.notes

    # Clear any active snooze when marked taken or skipped
    if status_update.status in ["taken", "skipped"]:
        log.snooze_until = None

    db.commit()
    db.refresh(log)

    med = db.query(Medicine).filter(Medicine.id == log.medicine_id).first()

    # Optional notification for taking medicine
    if status_update.status == "taken" and med:
        create_medicine_notification(
            db=db,
            user_id=current_user.id,
            title=f"Dose Recorded: {med.name}",
            message=f"You recorded taking your {med.dosage} dose of {med.name} at {log.logged_time.strftime('%I:%M %p')}.",
            notification_type="alert",
            medicine_id=med.id
        )

    return LogOut(
        id=log.id,
        user_id=log.user_id,
        medicine_id=log.medicine_id,
        schedule_id=log.schedule_id,
        scheduled_time=log.scheduled_time,
        logged_time=log.logged_time,
        status=log.status,
        notes=log.notes,
        snooze_until=log.snooze_until,
        medicine_name=med.name if med else "",
        medicine_dosage=med.dosage if med else "",
        medicine_form=med.form if med else "",
        instructions=med.instructions if med else "",
        created_at=log.created_at
    )

@router.post("/{log_id}/snooze", response_model=LogOut)
def snooze_log(
    log_id: int,
    snooze_data: LogSnooze,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    log = db.query(MedicineLog).filter(
        MedicineLog.id == log_id,
        MedicineLog.user_id == current_user.id
    ).first()
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dose log not found or access denied."
        )

    snooze_minutes = max(5, min(snooze_data.snooze_minutes, 180)) # between 5 mins and 3 hours
    log.snooze_until = datetime.now() + timedelta(minutes=snooze_minutes)
    db.commit()
    db.refresh(log)

    med = db.query(Medicine).filter(Medicine.id == log.medicine_id).first()
    return LogOut(
        id=log.id,
        user_id=log.user_id,
        medicine_id=log.medicine_id,
        schedule_id=log.schedule_id,
        scheduled_time=log.scheduled_time,
        logged_time=log.logged_time,
        status=log.status,
        notes=log.notes,
        snooze_until=log.snooze_until,
        medicine_name=med.name if med else "",
        medicine_dosage=med.dosage if med else "",
        medicine_form=med.form if med else "",
        instructions=med.instructions if med else "",
        created_at=log.created_at
    )
