from pydantic import BaseModel, Field


class StationBase(BaseModel):
    station_id: str
    name: str
    city: str | None = None
    state: str | None = None
    country: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    elevation: float | None = None
    timezone: str | None = None


class StationRead(StationBase):
    id: int

    model_config = {"from_attributes": True}
