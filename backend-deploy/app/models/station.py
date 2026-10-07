from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String

from app.database import Base


class Station(Base):
    __tablename__ = "stations"

    id = Column(Integer, primary_key=True, index=True)
    station_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    city = Column(String(100), index=True)
    state = Column(String(100), index=True)
    country = Column(String(100), index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    elevation = Column(Float)
    timezone = Column(String(80), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
