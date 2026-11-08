from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class DailyAdherence(BaseModel):
    date: str
    total: int
    taken: int
    skipped: int
    missed: int
    adherence_percentage: float

class CategoryStat(BaseModel):
    category: str
    count: int

class AdherenceReportOut(BaseModel):
    period: str # "week", "month", "all"
    start_date: str
    end_date: str
    total_scheduled: int
    total_taken: int
    total_skipped: int
    total_missed: int
    adherence_rate: float
    current_streak: int
    best_streak: int
    daily_history: List[DailyAdherence]
    category_distribution: List[CategoryStat]
    status_summary: Dict[str, int]
