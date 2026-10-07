from datetime import datetime

from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String

from app.database import Base


class DriftResult(Base):
    __tablename__ = "drift_results"

    id = Column(Integer, primary_key=True, index=True)
    station_id = Column(Integer, ForeignKey("stations.id"), nullable=False, index=True)
    variable = Column(String(50), nullable=False)
    baseline_start_date = Column(Date, nullable=False)
    baseline_end_date = Column(Date, nullable=False)
    current_start_date = Column(Date, nullable=False)
    current_end_date = Column(Date, nullable=False)
    baseline_mean = Column(Float)
    baseline_std = Column(Float)
    current_mean = Column(Float)
    current_std = Column(Float)
    ks_statistic = Column(Float)
    ks_p_value = Column(Float)
    psi_value = Column(Float)
    anomaly_count = Column(Integer)
    anomaly_percentage = Column(Float)
    drift_score = Column(Integer)
    drift_status = Column(String(30))
    analysis_timestamp = Column(DateTime, default=datetime.utcnow)
