from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import Base, engine
from app.models.alert import Alert  # noqa: F401
from app.models.drift_result import DriftResult  # noqa: F401
from app.models.session import UserSession  # noqa: F401
from app.models.station import Station  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.weather_data import WeatherData  # noqa: F401
from app.routes.admin import router as admin_router
from app.routes.alerts import router as alerts_router
from app.routes.auth import router as auth_router
from app.routes.dashboard import router as dashboard_router
from app.routes.data_import import router as data_import_router
from app.routes.drift import router as drift_router
from app.routes.locations import router as locations_router
from app.routes.weather import router as weather_router

app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(locations_router)
app.include_router(weather_router)
app.include_router(drift_router)
app.include_router(alerts_router)
app.include_router(dashboard_router)
app.include_router(data_import_router)
app.include_router(admin_router)

Base.metadata.create_all(bind=engine)

@app.get("/api/health")
def health():
    return {"status": "ok", "environment": settings.environment}

@app.get("/")
def root():
    return {"message": "Weather drift detection API is running"}
