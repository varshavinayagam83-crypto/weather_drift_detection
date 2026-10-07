from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.drift.engine import run_drift_analysis
from app.models.drift_result import DriftResult
from app.models.weather_data import WeatherData

router = APIRouter(prefix="/api/drift", tags=["drift"])


@router.post("/analyze")
def analyze(payload: dict, db: Session = Depends(get_db)):
    station_id = payload["station_id"]
    variable = payload.get("variable", "temperature_avg")
    baseline_start = payload.get("baseline_start")
    current_start = payload.get("current_start")
    if baseline_start and current_start:
        baseline_start = date.fromisoformat(baseline_start)
        current_start = date.fromisoformat(current_start)
        baseline_end = date.fromisoformat(payload.get("baseline_end"))
        current_end = date.fromisoformat(payload.get("current_end"))
    rows = db.query(WeatherData).filter(WeatherData.station_id == station_id).order_by(WeatherData.observation_date.asc()).all()
    frame = [
        {
            "observation_date": r.observation_date,
            "temperature_avg": r.temperature_avg,
            "rainfall": r.rainfall,
            "humidity": r.humidity,
            "pressure": r.pressure,
            "wind_speed": r.wind_speed,
        }
        for r in rows
    ]
    metrics = run_drift_analysis(__import__("pandas").DataFrame(frame), variable, baseline_start, baseline_end, current_start, current_end)
    result = DriftResult(
        station_id=station_id,
        variable=variable,
        baseline_start_date=baseline_start,
        baseline_end_date=baseline_end,
        current_start_date=current_start,
        current_end_date=current_end,
        baseline_mean=metrics.get("baseline_mean"),
        current_mean=metrics.get("current_mean"),
        baseline_std=metrics.get("baseline_std"),
        current_std=metrics.get("current_std"),
        ks_statistic=metrics.get("ks_statistic"),
        ks_p_value=metrics.get("ks_p_value"),
        psi_value=metrics.get("psi_value"),
        anomaly_count=metrics.get("anomaly_count"),
        anomaly_percentage=metrics.get("anomaly_percentage"),
        drift_score=metrics.get("drift_score"),
        drift_status=metrics.get("drift_status"),
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return {"result": result, **metrics}


@router.get("/{station_id}")
def drift_for_station(station_id: int, db: Session = Depends(get_db)):
    return db.query(DriftResult).filter(DriftResult.station_id == station_id).order_by(DriftResult.analysis_timestamp.desc()).first()


@router.get("/history")
def drift_history(db: Session = Depends(get_db)):
    return db.query(DriftResult).order_by(DriftResult.analysis_timestamp.desc()).all()
