from sqlalchemy.orm import Session

from app.models.alert import Alert


def create_alert(db: Session, station_id: int, drift_result_id: int | None, variable: str, severity: str, title: str, message: str):
    alert = Alert(
        station_id=station_id,
        drift_result_id=drift_result_id,
        variable=variable,
        severity=severity,
        title=title,
        message=message,
        is_read=False,
        is_resolved=False,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def get_alerts(db: Session):
    return db.query(Alert).order_by(Alert.created_at.desc()).all()
