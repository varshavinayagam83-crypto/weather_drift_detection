from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.station import Station
from app.models.weather_data import WeatherData
from app.services.weather_service import get_current_weather, get_weather_history

router = APIRouter(prefix="/api/weather", tags=["weather"])


@router.get("/current/{station_id}")
def current_weather(station_id: int, db: Session = Depends(get_db)):
    return get_current_weather(db, station_id)


@router.get("/history/{station_id}")
def weather_history(station_id: int, days: int = Query(default=30), db: Session = Depends(get_db)):
    rows = get_weather_history(db, station_id, days)
    return {"items": rows, "count": len(rows)}


@router.get("/{station_id}/summary")
def summary(station_id: int, db: Session = Depends(get_db)):
    station = db.query(Station).filter(Station.id == station_id).first()
    weather = db.query(WeatherData).filter(WeatherData.station_id == station_id, WeatherData.observation_date <= date.today()).order_by(WeatherData.observation_date.desc()).first()
    return {
        "station_name": station.name if station else "Unknown",
        "country": station.country if station else None,
        "temperature": weather.temperature_avg if weather else None,
        "humidity": weather.humidity if weather else None,
        "pressure": weather.pressure if weather else None,
        "wind_speed": weather.wind_speed if weather else None,
        "rainfall": weather.rainfall if weather else None,
    }
