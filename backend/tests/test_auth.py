from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get('/api/health')
    assert response.status_code == 200


def test_register_and_login():
    username = f'user-{uuid4().hex}'
    payload = {'username': username, 'email': f'{username}@example.com', 'password': 'StrongPass1!'}
    r1 = client.post('/api/auth/register', json=payload)
    assert r1.status_code == 200
    duplicate = client.post('/api/auth/register', json=payload)
    assert duplicate.status_code == 409
    r2 = client.post('/api/auth/login', json={'username': username, 'password': 'StrongPass1!'})
    assert r2.status_code == 200
    assert 'access_token' in r2.json()


def test_protected_endpoint_requires_auth():
    r = client.get('/api/alerts')
    assert r.status_code == 401


def test_role_unauthorized():
    response = client.get('/api/admin/users')
    assert response.status_code == 401
