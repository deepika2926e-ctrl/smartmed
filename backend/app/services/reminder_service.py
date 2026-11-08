import logging
from datetime import datetime, date, time, timedelta, timezone
from typing import List
from sqlalchemy.orm import Session
from app.models.medicine import Medicine
from app.models.schedule import MedicineSchedule
from app.models.log import MedicineLog
from app.models.notification import Notification

logger = logging.getLogger(__name__)

DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

def generate_daily_logs_for_user(db: Session, user_id: int, target_date: date = None) -> List[MedicineLog]:
    """
    Ensures that for target_date (defaulting to today), every active medicine schedule
    matching the day of the week has a corresponding MedicineLog record.
    """
    if target_date is None:
        target_date = date.today()
    
    current_day_name = DAY_NAMES[target_date.weekday()]
    
    # Fetch user's active schedules where the medicine is also active
    active_schedules = (
        db.query(MedicineSchedule)
        .join(Medicine, Medicine.id == MedicineSchedule.medicine_id)
        .filter(
            MedicineSchedule.user_id == user_id,
            MedicineSchedule.is_active == True,
            Medicine.status == "active",
            Medicine.start_date <= target_date,
            (Medicine.end_date == None) | (Medicine.end_date >= target_date),
            (MedicineSchedule.start_date == None) | (MedicineSchedule.start_date <= target_date),
            (MedicineSchedule.end_date == None) | (MedicineSchedule.end_date >= target_date)
        )
        .all()
    )

    created_logs = []
    
    for sched in active_schedules:
        # Check day-of-week match
        allowed_days = [d.strip() for d in sched.days_of_week.split(",") if d.strip()]
        if current_day_name not in allowed_days and "Daily" not in allowed_days and len(allowed_days) > 0:
            continue

        # Parse reminder_time (e.g., "08:00")
        try:
            hour_str, min_str = sched.reminder_time.split(":")
            dose_time = time(int(hour_str), int(min_str))
            scheduled_dt = datetime.combine(target_date, dose_time)
        except Exception:
            continue

        # Check if log already exists for this schedule and target_date
        existing = (
            db.query(MedicineLog)
            .filter(
                MedicineLog.user_id == user_id,
                MedicineLog.medicine_id == sched.medicine_id,
                MedicineLog.schedule_id == sched.id,
                MedicineLog.scheduled_time >= datetime.combine(target_date, time.min),
                MedicineLog.scheduled_time <= datetime.combine(target_date, time.max)
            )
            .first()
        )

        if not existing:
            new_log = MedicineLog(
                user_id=user_id,
                medicine_id=sched.medicine_id,
                schedule_id=sched.id,
                scheduled_time=scheduled_dt,
                status="pending"
            )
            db.add(new_log)
            created_logs.append(new_log)

    if created_logs:
        db.commit()

    # Automatically mark overdue pending logs as missed (e.g., scheduled more than 3 hours ago)
    now = datetime.now()
    overdue_cutoff = now - timedelta(hours=3)
    
    overdue_logs = (
        db.query(MedicineLog)
        .filter(
            MedicineLog.user_id == user_id,
            MedicineLog.status == "pending",
            MedicineLog.scheduled_time < overdue_cutoff
        )
        .all()
    )
    for o_log in overdue_logs:
        o_log.status = "missed"
    
    if overdue_logs:
        db.commit()

    # Return all today's logs for this user
    today_start = datetime.combine(target_date, time.min)
    today_end = datetime.combine(target_date, time.max)
    
    return (
        db.query(MedicineLog)
        .filter(
            MedicineLog.user_id == user_id,
            MedicineLog.scheduled_time >= today_start,
            MedicineLog.scheduled_time <= today_end
        )
        .order_by(MedicineLog.scheduled_time.asc())
        .all()
    )

def create_medicine_notification(db: Session, user_id: int, title: str, message: str, notification_type: str = "reminder", medicine_id: int = None):
    """Helper to create and persist in-app notification."""
    notif = Notification(
        user_id=user_id,
        medicine_id=medicine_id,
        title=title,
        message=message,
        notification_type=notification_type,
        is_read=False
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif
