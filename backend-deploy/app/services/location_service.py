from sqlalchemy.orm import Session

from app.models.station import Station


def search_stations(db: Session, query: str | None = None, limit: int = 25):
    q = db.query(Station)
    if query:
        like = f"%{query}%"
        q = q.filter(
            (Station.station_id.ilike(like))
            | (Station.name.ilike(like))
            | (Station.city.ilike(like))
            | (Station.state.ilike(like))
            | (Station.country.ilike(like))
        )
    return q.order_by(Station.country, Station.city, Station.name).limit(limit).all()


def get_station_by_id(db: Session, station_id: int) -> Station | None:
    return db.query(Station).filter(Station.id == station_id).first()
