from datetime import datetime

from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String

from app.database import Base


class WeatherData(Base):
    __tablename__ = "weather_data"

    id = Column(Integer, primary_key=True, index=True)
    station_id = Column(Integer, ForeignKey("stations.id"), nullable=False, index=True)
    observation_date = Column(Date, nullable=False, index=True)
    temperature_max = Column(Float, nullable=True)
    temperature_min = Column(Float, nullable=True)
    temperature_avg = Column(Float, nullable=True)
    rainfall = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    pressure = Column(Float, nullable=True)
    wind_speed = Column(Float, nullable=True)
    source = Column(String(50), default="NOAA")
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = ({"sqlite_autoincrement": True},)
