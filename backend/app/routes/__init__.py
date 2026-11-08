from app.routes.auth import router as auth_router
from app.routes.users import router as users_router
from app.routes.medicines import router as medicines_router
from app.routes.medicine_info import router as medicine_info_router
from app.routes.schedules import router as schedules_router
from app.routes.logs import router as logs_router
from app.routes.notifications import router as notifications_router
from app.routes.prescriptions import router as prescriptions_router
from app.routes.reports import router as reports_router
from app.routes.settings import router as settings_router

__all__ = [
    "auth_router",
    "users_router",
    "medicines_router",
    "medicine_info_router",
    "schedules_router",
    "logs_router",
    "notifications_router",
    "prescriptions_router",
    "reports_router",
    "settings_router"
]
