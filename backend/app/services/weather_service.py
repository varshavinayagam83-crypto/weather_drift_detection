from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models.station import Station
from app.models.weather_data import WeatherData


def get_current_weather(db: Session, station_id: int):
    station = db.query(Station).filter(Station.id == station_id).first()
    if not station:
        return {
            "station_id": station_id,
            "station": None,
            "temperature": None,
            "condition": "Unknown",
            "humidity": None,
            "wind_speed": None,
            "pressure": None,
            "rainfall": None,
        }
    today = date.today()
    latest = db.query(WeatherData).filter(WeatherData.station_id == station_id, WeatherData.observation_date <= today).order_by(WeatherData.observation_date.desc()).first()
    if latest is None:
        return {
            "station": station,
            "temperature": 22.0,
            "condition": "Unknown",
            "humidity": 58,
            "wind_speed": 12.0,
            "pressure": 1013.0,
            "rainfall": 0.0,
        }
    return {
        "station": station,
        "temperature": latest.temperature_avg or ((latest.temperature_max or 0) + (latest.temperature_min or 0)) / 2,
        "condition": "Sunny" if (latest.temperature_avg or 25) > 25 else "Cloudy",
        "humidity": latest.humidity,
        "wind_speed": latest.wind_speed,
        "pressure": latest.pressure,
        "rainfall": latest.rainfall,
    }


def get_weather_history(db: Session, station_id: int, days: int = 30):
    end = date.today()
    start = end - timedelta(days=days)
    rows = db.query(WeatherData).filter(WeatherData.station_id == station_id, WeatherData.observation_date.between(start, end)).order_by(WeatherData.observation_date.asc()).all()
    return rows
