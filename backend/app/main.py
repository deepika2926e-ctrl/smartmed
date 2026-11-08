import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, RedirectResponse

from app.config import settings
from app.database import engine, Base, SessionLocal
import app.models  # Ensure all models are registered
from app.routes import (
    auth_router,
    users_router,
    medicines_router,
    medicine_info_router,
    schedules_router,
    logs_router,
    notifications_router,
    prescriptions_router,
    reports_router,
    settings_router
)
from app.services.sample_data_seed import seed_educational_medicines

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("smartmed")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    logger.info("Initializing SmartMed database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables verified/created successfully.")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")

    # Seed educational medicine library
    try:
        db = SessionLocal()
        seed_educational_medicines(db)
        db.close()
    except Exception as e:
        logger.error(f"Error seeding educational medicines: {e}")

    # Ensure uploads directory
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    logger.info(f"Uploads directory verified at: {settings.UPLOAD_DIR}")

    yield

    # Shutdown actions
    logger.info("Shutting down SmartMed API server.")

app = FastAPI(
    title="SmartMed API",
    description="Advanced Medicine Schedule Reminder System REST API with educational medicine library, schedules, adherence tracking, and notifications.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
if "*" in origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Mount Uploads directory
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include Routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(medicines_router)
app.include_router(medicine_info_router)
app.include_router(schedules_router)
app.include_router(logs_router)
app.include_router(notifications_router)
app.include_router(prescriptions_router)
app.include_router(reports_router)
app.include_router(settings_router)

# Frontend static serving (optional integration for single-origin hosting or preview)
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend"))
if os.path.exists(frontend_dir):
    app.mount("/app", StaticFiles(directory=frontend_dir, html=True), name="frontend_app")

@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "version": "1.0.0"
    }

@app.get("/", include_in_schema=False)
def root_redirect():
    # If frontend exists, redirect to app homepage; otherwise docs
    if os.path.exists(frontend_dir):
        return RedirectResponse(url="/app/index.html")
    return RedirectResponse(url="/docs")
