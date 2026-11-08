from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta, time
from app.database import get_db
from app.models.medicine import Medicine
from app.models.schedule import MedicineSchedule
from app.models.log import MedicineLog
from app.models.user import User
from app.schemas.report import AdherenceReportOut
from app.security.auth_bearer import get_current_user
from app.services.report_service import calculate_adherence_report
from app.services.reminder_service import generate_daily_logs_for_user

router = APIRouter(prefix="/api/reports", tags=["Reports & Analytics"])

@router.get("/adherence", response_model=AdherenceReportOut)
def get_adherence_report(
    period: str = Query("week", description="week, month, or all"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return calculate_adherence_report(db, current_user.id, period=period)

@router.get("/dashboard-summary")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Total medicines
    total_meds = db.query(Medicine).filter(Medicine.user_id == current_user.id).count()
    active_meds = db.query(Medicine).filter(
        Medicine.user_id == current_user.id,
        Medicine.status == "active"
    ).count()
    completed_meds = db.query(Medicine).filter(
        Medicine.user_id == current_user.id,
        Medicine.status == "completed"
    ).count()

    # Ensure today's logs are generated
    today_logs = generate_daily_logs_for_user(db, current_user.id, date.today())
    today_total = len(today_logs)
    today_taken = sum(1 for l in today_logs if l.status == "taken")
    today_pending = sum(1 for l in today_logs if l.status == "pending")
    today_missed = sum(1 for l in today_logs if l.status == "missed")
    today_skipped = sum(1 for l in today_logs if l.status == "skipped")

    # Adherence rates
    weekly_report = calculate_adherence_report(db, current_user.id, period="week")
    monthly_report = calculate_adherence_report(db, current_user.id, period="month")

    # Upcoming pending doses today
    now = datetime.now()
    upcoming_today = []
    for l in today_logs:
        if l.status == "pending":
            med = db.query(Medicine).filter(Medicine.id == l.medicine_id).first()
            upcoming_today.append({
                "id": l.id,
                "medicine_name": med.name if med else "Medicine",
                "dosage": med.dosage if med else "",
                "form": med.form if med else "",
                "scheduled_time": l.scheduled_time.strftime("%I:%M %p"),
                "instructions": med.instructions if med else "",
                "is_overdue": l.scheduled_time < now
            })

    # Recent history (last 5 logs)
    recent_logs_query = (
        db.query(MedicineLog, Medicine.name, Medicine.dosage)
        .join(Medicine, Medicine.id == MedicineLog.medicine_id)
        .filter(MedicineLog.user_id == current_user.id)
        .order_by(MedicineLog.scheduled_time.desc())
        .limit(5)
        .all()
    )
    recent_activity = [
        {
            "id": l.id,
            "medicine_name": name,
            "dosage": dosage,
            "status": l.status,
            "time": l.scheduled_time.strftime("%b %d, %I:%M %p"),
            "logged_time": l.logged_time.strftime("%I:%M %p") if l.logged_time else None
        }
        for l, name, dosage in recent_logs_query
    ]

    return {
        "total_medicines": total_meds,
        "active_medicines": active_meds,
        "completed_medicines": completed_meds,
        "today_total": today_total,
        "today_taken": today_taken,
        "today_pending": today_pending,
        "today_missed": today_missed,
        "today_skipped": today_skipped,
        "weekly_adherence_rate": weekly_report["adherence_rate"],
        "monthly_adherence_rate": monthly_report["adherence_rate"],
        "current_streak": weekly_report["current_streak"],
        "best_streak": weekly_report["best_streak"],
        "upcoming_today": upcoming_today[:4],
        "recent_activity": recent_activity,
        "weekly_chart": weekly_report["daily_history"],
        "categories": weekly_report["category_distribution"]
    }
