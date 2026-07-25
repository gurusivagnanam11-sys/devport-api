def test_register_user(client):
    response = client.post("/auth/register", json={
        "email": "alice@example.com",
        "password": "securepassword123",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "alice@example.com"
    assert "id" in data
    assert "password" not in data
    assert "password_hash" not in data


def test_register_duplicate_email_rejected(client):
    client.post("/auth/register", json={"email": "bob@example.com", "password": "pass1234"})
    response = client.post("/auth/register", json={"email": "bob@example.com", "password": "otherpass"})
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_login_success(client):
    client.post("/auth/register", json={"email": "carol@example.com", "password": "mypassword"})
    response = client.post("/auth/login", json={"email": "carol@example.com", "password": "mypassword"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password_rejected(client):
    client.post("/auth/register", json={"email": "dave@example.com", "password": "correctpass"})
    response = client.post("/auth/login", json={"email": "dave@example.com", "password": "wrongpass"})
    assert response.status_code == 401


def test_login_nonexistent_user_rejected(client):
    response = client.post("/auth/login", json={"email": "nobody@example.com", "password": "anything"})
    assert response.status_code == 401


def test_protected_route_requires_token(client):
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_protected_route_with_valid_token(client):
    client.post("/auth/register", json={"email": "eve@example.com", "password": "pass1234"})
    login = client.post("/auth/login", json={"email": "eve@example.com", "password": "pass1234"})
    token = login.json()["access_token"]

    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "eve@example.com"


def test_protected_route_rejects_invalid_token(client):
    response = client.get("/auth/me", headers={"Authorization": "Bearer garbage.invalid.token"})
    assert response.status_code == 401
