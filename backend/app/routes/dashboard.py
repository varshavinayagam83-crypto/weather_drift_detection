from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.alert import Alert
from app.models.drift_result import DriftResult
from app.models.station import Station
from app.models.weather_data import WeatherData

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary/{station_id}")
def summary(station_id: int, db: Session = Depends(get_db)):
    station = db.query(Station).filter(Station.id == station_id).first()
    weather = db.query(WeatherData).filter(WeatherData.station_id == station_id).order_by(WeatherData.observation_date.desc()).first()
    drift = db.query(DriftResult).filter(DriftResult.station_id == station_id).order_by(DriftResult.analysis_timestamp.desc()).first()
    alert_count = db.query(Alert).filter(Alert.station_id == station_id, Alert.is_resolved == False).count()
    return {
        "station": station,
        "weather": weather,
        "latest_drift": drift,
        "active_alerts": alert_count,
    }
