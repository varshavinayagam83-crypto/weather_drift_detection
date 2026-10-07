from datetime import date

from pydantic import BaseModel, Field


class DriftAnalysisRequest(BaseModel):
    station_id: int
    variable: str = "temperature_avg"
    baseline_start: date
    baseline_end: date
    current_start: date
    current_end: date


class DriftAnalysisResult(BaseModel):
    station_id: int
    variable: str
    baseline_mean: float | None = None
    current_mean: float | None = None
    baseline_std: float | None = None
    current_std: float | None = None
    ks_statistic: float | None = None
    ks_p_value: float | None = None
    psi_value: float | None = None
    anomaly_count: int | None = None
    anomaly_percentage: float | None = None
    drift_score: int | None = None
    drift_status: str | None = None
    message: str | None = None

    model_config = {"from_attributes": True}
