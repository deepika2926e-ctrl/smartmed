from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timedelta, time
from app.database import get_db
from app.models.medicine import Medicine
from app.models.schedule import MedicineSchedule
from app.models.log import MedicineLog
from app.models.user import User
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate, ScheduleOut
from app.schemas.log import LogOut
from app.security.auth_bearer import get_current_user
from app.services.reminder_service import generate_daily_logs_for_user

router = APIRouter(prefix="/api/schedules", tags=["Medicine Schedules"])

@router.get("", response_model=List[ScheduleOut])
def list_schedules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    results = (
        db.query(MedicineSchedule, Medicine.name, Medicine.form, Medicine.dosage)
        .join(Medicine, Medicine.id == MedicineSchedule.medicine_id)
        .filter(MedicineSchedule.user_id == current_user.id)
        .order_by(MedicineSchedule.reminder_time.asc())
        .all()
    )

    out = []
    for sched, med_name, med_form, med_dosage in results:
        sched_dict = {
            "id": sched.id,
            "user_id": sched.user_id,
            "medicine_id": sched.medicine_id,
            "reminder_time": sched.reminder_time,
            "time_of_day": sched.time_of_day,
            "days_of_week": sched.days_of_week,
            "dosage_quantity": sched.dosage_quantity,
            "is_active": sched.is_active,
            "start_date": sched.start_date,
            "end_date": sched.end_date,
            "medicine_name": med_name,
            "medicine_form": med_form,
            "medicine_dosage": med_dosage,
            "created_at": sched.created_at,
            "updated_at": sched.updated_at
        }
        out.append(ScheduleOut(**sched_dict))
    return out

@router.post("", response_model=ScheduleOut, status_code=status.HTTP_201_CREATED)
def create_schedule(
    sched_in: ScheduleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify medicine belongs to current user
    med = db.query(Medicine).filter(
        Medicine.id == sched_in.medicine_id,
        Medicine.user_id == current_user.id
    ).first()
    if not med:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicine not found or access denied."
        )

    # Determine time of day if default or calculate from hour
    tod = sched_in.time_of_day
    if not tod or tod == "custom":
        try:
            hour = int(sched_in.reminder_time.split(":")[0])
            if 5 <= hour < 12:
                tod = "morning"
            elif 12 <= hour < 17:
                tod = "afternoon"
            elif 17 <= hour < 21:
                tod = "evening"
            else:
                tod = "night"
        except Exception:
            tod = "custom"

    new_sched = MedicineSchedule(
        user_id=current_user.id,
        medicine_id=sched_in.medicine_id,
        reminder_time=sched_in.reminder_time,
        time_of_day=tod,
        days_of_week=sched_in.days_of_week,
        dosage_quantity=sched_in.dosage_quantity,
        is_active=sched_in.is_active,
        start_date=sched_in.start_date or med.start_date,
        end_date=sched_in.end_date or med.end_date
    )
    db.add(new_sched)
    db.commit()
    db.refresh(new_sched)

    # Trigger today's log refresh for user
    generate_daily_logs_for_user(db, current_user.id)

    return ScheduleOut(
        id=new_sched.id,
        user_id=new_sched.user_id,
        medicine_id=new_sched.medicine_id,
        reminder_time=new_sched.reminder_time,
        time_of_day=new_sched.time_of_day,
        days_of_week=new_sched.days_of_week,
        dosage_quantity=new_sched.dosage_quantity,
        is_active=new_sched.is_active,
        start_date=new_sched.start_date,
        end_date=new_sched.end_date,
        medicine_name=med.name,
        medicine_form=med.form,
        medicine_dosage=med.dosage,
        created_at=new_sched.created_at,
        updated_at=new_sched.updated_at
    )

@router.get("/today", response_model=List[LogOut])
def get_today_medicines(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generates and returns today's dose logs for the current user."""
    logs = generate_daily_logs_for_user(db, current_user.id, date.today())
    
    out = []
    for l in logs:
        med = db.query(Medicine).filter(Medicine.id == l.medicine_id).first()
        out.append(LogOut(
            id=l.id,
            user_id=l.user_id,
            medicine_id=l.medicine_id,
            schedule_id=l.schedule_id,
            scheduled_time=l.scheduled_time,
            logged_time=l.logged_time,
            status=l.status,
            notes=l.notes,
            snooze_until=l.snooze_until,
            medicine_name=med.name if med else "Unknown",
            medicine_dosage=med.dosage if med else "",
            medicine_form=med.form if med else "",
            instructions=med.instructions if med else "",
            created_at=l.created_at
        ))
    return out

@router.get("/upcoming")
def get_upcoming_reminders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Returns today's remaining doses and next 3 days' schedule projection."""
    now = datetime.now()
    today_logs = generate_daily_logs_for_user(db, current_user.id, date.today())
    
    # Filter today's upcoming/pending doses
    pending_today = [
        {
            "id": l.id,
            "medicine_id": l.medicine_id,
            "medicine_name": l.medicine.name if l.medicine else "",
            "dosage": l.medicine.dosage if l.medicine else "",
            "form": l.medicine.form if l.medicine else "",
            "instructions": l.medicine.instructions if l.medicine else "",
            "scheduled_time": l.scheduled_time.strftime("%I:%M %p"),
            "full_time": l.scheduled_time.isoformat(),
            "status": l.status,
            "is_overdue": l.scheduled_time < now and l.status == "pending"
        }
        for l in today_logs
    ]

    # Active schedules summary
    schedules = (
        db.query(MedicineSchedule)
        .join(Medicine, Medicine.id == MedicineSchedule.medicine_id)
        .filter(MedicineSchedule.user_id == current_user.id, MedicineSchedule.is_active == True)
        .all()
    )
    
    sched_list = [
        {
            "id": s.id,
            "medicine_name": s.medicine.name if s.medicine else "",
            "dosage_quantity": s.dosage_quantity,
            "reminder_time": s.reminder_time,
            "time_of_day": s.time_of_day,
            "days_of_week": s.days_of_week
        }
        for s in schedules
    ]

    return {
        "today_pending": pending_today,
        "active_schedules_count": len(schedules),
        "schedules": sched_list
    }

@router.put("/{schedule_id}", response_model=ScheduleOut)
def update_schedule(
    schedule_id: int,
    sched_update: ScheduleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sched = db.query(MedicineSchedule).filter(
        MedicineSchedule.id == schedule_id,
        MedicineSchedule.user_id == current_user.id
    ).first()
    if not sched:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found or access denied."
        )

    update_dict = sched_update.dict(exclude_unset=True)
    for field, val in update_dict.items():
        setattr(sched, field, val)

    db.commit()
    db.refresh(sched)

    med = db.query(Medicine).filter(Medicine.id == sched.medicine_id).first()
    return ScheduleOut(
        id=sched.id,
        user_id=sched.user_id,
        medicine_id=sched.medicine_id,
        reminder_time=sched.reminder_time,
        time_of_day=sched.time_of_day,
        days_of_week=sched.days_of_week,
        dosage_quantity=sched.dosage_quantity,
        is_active=sched.is_active,
        start_date=sched.start_date,
        end_date=sched.end_date,
        medicine_name=med.name if med else "",
        medicine_form=med.form if med else "",
        medicine_dosage=med.dosage if med else "",
        created_at=sched.created_at,
        updated_at=sched.updated_at
    )

@router.delete("/{schedule_id}")
def delete_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sched = db.query(MedicineSchedule).filter(
        MedicineSchedule.id == schedule_id,
        MedicineSchedule.user_id == current_user.id
    ).first()
    if not sched:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found or access denied."
        )

    db.delete(sched)
    db.commit()
    return {"message": "Schedule deleted successfully."}
