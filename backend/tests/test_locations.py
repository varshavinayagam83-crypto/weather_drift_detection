from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_locations_endpoint():
    response = client.get('/api/locations')
    assert response.status_code == 200
    assert isinstance(response.json().get('items'), list)
