from datetime import datetime

from sqlalchemy.orm import Session

from app.models.station import Station
from app.models.weather_data import WeatherData


def import_station_rows(db: Session, rows):
    inserted = 0
    for row in rows:
        existing = db.query(Station).filter(Station.station_id == row.get("station_id")).first()
        if existing is None:
            station = Station(
                station_id=row.get("station_id"),
                name=row.get("name") or row.get("station_id"),
                city=row.get("city"),
                state=row.get("state"),
                country=row.get("country"),
                latitude=row.get("latitude"),
                longitude=row.get("longitude"),
                elevation=row.get("elevation"),
                timezone=row.get("timezone"),
            )
            db.add(station)
            db.commit()
            db.refresh(station)
            inserted += 1
    return {"inserted": inserted}


def import_weather_rows(db: Session, station_id: int, rows):
    inserted = 0
    for row in rows:
        existing = db.query(WeatherData).filter(WeatherData.station_id == station_id, WeatherData.observation_date == row.get("date")).first()
        if existing is None:
            payload = WeatherData(
                station_id=station_id,
                observation_date=row.get("date"),
                temperature_max=row.get("temperature_max"),
                temperature_min=row.get("temperature_min"),
                temperature_avg=row.get("temperature_avg"),
                rainfall=row.get("rainfall"),
                humidity=row.get("humidity"),
                pressure=row.get("pressure"),
                wind_speed=row.get("wind_speed"),
                source=row.get("source", "NOAA"),
                created_at=datetime.utcnow(),
            )
            db.add(payload)
            inserted += 1
    db.commit()
    return {"inserted": inserted}
