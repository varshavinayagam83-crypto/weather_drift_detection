from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_current_weather_missing_station():
    response = client.get('/api/weather/current/999999')
    assert response.status_code == 200
    assert response.json() is not None
