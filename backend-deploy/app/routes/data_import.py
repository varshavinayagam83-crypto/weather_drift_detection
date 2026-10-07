from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.data_import_service import import_station_rows, import_weather_rows

router = APIRouter(prefix="/api/data", tags=["data-import"])


@router.post("/import")
def import_data(payload: dict, db: Session = Depends(get_db)):
    if payload.get("stations"):
        result = import_station_rows(db, payload["stations"])
        return result
    if payload.get("station_id") and payload.get("weather_records"):
        result = import_weather_rows(db, payload["station_id"], payload["weather_records"])
        return result
    return {"message": "No records supplied"}
