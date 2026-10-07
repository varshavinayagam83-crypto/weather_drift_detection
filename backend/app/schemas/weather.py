from datetime import date, datetime

from pydantic import BaseModel


class WeatherObservation(BaseModel):
    id: int | None = None
    station_id: int
    observation_date: date
    temperature_max: float | None = None
    temperature_min: float | None = None
    temperature_avg: float | None = None
    rainfall: float | None = None
    humidity: float | None = None
    pressure: float | None = None
    wind_speed: float | None = None
    source: str = "NOAA"

    model_config = {"from_attributes": True}


class WeatherSummary(BaseModel):
    station_id: int
    station_name: str
    country: str | None = None
    current_temperature: float | None = None
    condition: str = "Unknown"
    humidity: float | None = None
    wind_speed: float | None = None
    pressure: float | None = None
    rainfall: float | None = None
