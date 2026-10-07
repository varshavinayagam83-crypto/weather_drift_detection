from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.location_service import search_stations

router = APIRouter(prefix="/api/locations", tags=["locations"])


@router.get("")
def list_locations(q: str | None = Query(default=None), db: Session = Depends(get_db)):
    stations = search_stations(db, q)
    return {"items": stations, "count": len(stations)}


@router.get("/{station_id}")
def station_detail(station_id: int, db: Session = Depends(get_db)):
    station = db.query(__import__("app.models.station", fromlist=["Station"]).Station).filter(__import__("app.models.station", fromlist=["Station"]).Station.id == station_id).first()
    if station is None:
        return {"detail": "Station not found"}
    return station
