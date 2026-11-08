from datetime import date, datetime, timedelta, time
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.log import MedicineLog
from app.models.medicine import Medicine

def calculate_adherence_report(db: Session, user_id: int, period: str = "week") -> Dict[str, Any]:
    today = date.today()
    
    if period == "week":
        start_date = today - timedelta(days=6)
    elif period == "month":
        start_date = today - timedelta(days=29)
    else: # "all" or custom
        start_date = today - timedelta(days=90)
    
    start_dt = datetime.combine(start_date, time.min)
    end_dt = datetime.combine(today, time.max)

    logs = (
        db.query(MedicineLog)
        .filter(
            MedicineLog.user_id == user_id,
            MedicineLog.scheduled_time >= start_dt,
            MedicineLog.scheduled_time <= end_dt
        )
        .order_by(MedicineLog.scheduled_time.asc())
        .all()
    )

    total_scheduled = len(logs)
    taken = sum(1 for l in logs if l.status == "taken")
    skipped = sum(1 for l in logs if l.status == "skipped")
    missed = sum(1 for l in logs if l.status == "missed")
    pending = sum(1 for l in logs if l.status == "pending")

    completed_doses = taken + skipped + missed
    if completed_doses > 0:
        adherence_rate = round((taken / completed_doses) * 100, 1)
    elif total_scheduled > 0:
        adherence_rate = 100.0
    else:
        adherence_rate = 100.0

    # Build daily history map
    daily_map: Dict[str, Dict[str, int]] = {}
    current_iter = start_date
    while current_iter <= today:
        d_str = current_iter.strftime("%Y-%m-%d")
        daily_map[d_str] = {"total": 0, "taken": 0, "skipped": 0, "missed": 0}
        current_iter += timedelta(days=1)

    for l in logs:
        d_str = l.scheduled_time.strftime("%Y-%m-%d")
        if d_str in daily_map:
            daily_map[d_str]["total"] += 1
            if l.status in daily_map[d_str]:
                daily_map[d_str][l.status] += 1

    daily_history = []
    current_streak = 0
    best_streak = 0
    temp_streak = 0

    for d_str, counts in sorted(daily_map.items()):
        tot = counts["total"]
        t = counts["taken"]
        s = counts["skipped"]
        m = counts["missed"]
        rate = round((t / (t + s + m) * 100), 1) if (t + s + m) > 0 else (100.0 if tot == 0 else 0.0)
        daily_history.append({
            "date": d_str,
            "total": tot,
            "taken": t,
            "skipped": s,
            "missed": m,
            "adherence_percentage": rate
        })

        # Calculate streak: a day counts if total > 0 and taken == total (or 100%)
        if tot > 0 and (t / tot >= 0.8): # 80%+ adherence counts toward streak
            temp_streak += 1
            if temp_streak > best_streak:
                best_streak = temp_streak
        elif tot > 0:
            temp_streak = 0

    current_streak = temp_streak

    # Category distribution
    categories_count: Dict[str, int] = {}
    medicines = db.query(Medicine).filter(Medicine.user_id == user_id).all()
    for med in medicines:
        cat = med.category or "General"
        categories_count[cat] = categories_count.get(cat, 0) + 1

    category_distribution = [{"category": k, "count": v} for k, v in categories_count.items()]

    return {
        "period": period,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": today.strftime("%Y-%m-%d"),
        "total_scheduled": total_scheduled,
        "total_taken": taken,
        "total_skipped": skipped,
        "total_missed": missed,
        "adherence_rate": adherence_rate,
        "current_streak": current_streak,
        "best_streak": best_streak,
        "daily_history": daily_history,
        "category_distribution": category_distribution,
        "status_summary": {
            "taken": taken,
            "skipped": skipped,
            "missed": missed,
            "pending": pending
        }
    }
