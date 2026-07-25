def _register_and_login(client, email="admin@example.com", password="pass1234"):
    client.post("/auth/register", json={"email": email, "password": password})
    login = client.post("/auth/login", json={"email": email, "password": password})
    return login.json()["access_token"]


def _auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_create_workspace(client):
    token = _register_and_login(client)
    response = client.post("/workspaces/", json={"name": "Acme Corp"}, headers=_auth_headers(token))
    assert response.status_code == 201
    assert response.json()["name"] == "Acme Corp"


def test_creator_is_automatically_admin(client):
    token = _register_and_login(client)
    ws = client.post("/workspaces/", json={"name": "Acme Corp"}, headers=_auth_headers(token)).json()

    members = client.get(f"/workspaces/{ws['id']}/members", headers=_auth_headers(token)).json()
    assert len(members) == 1
    assert members[0]["role"] == "admin"


def test_non_member_cannot_access_workspace(client):
    token_a = _register_and_login(client, "usera@example.com")
    token_b = _register_and_login(client, "userb@example.com")

    ws = client.post("/workspaces/", json={"name": "A's workspace"}, headers=_auth_headers(token_a)).json()

    response = client.get(f"/workspaces/{ws['id']}", headers=_auth_headers(token_b))
    assert response.status_code == 404


def test_member_cannot_delete_workspace(client):
    admin_token = _register_and_login(client, "admin2@example.com")
    ws = client.post("/workspaces/", json={"name": "Test WS"}, headers=_auth_headers(admin_token)).json()

    member_token = _register_and_login(client, "member2@example.com")
    client.post(
        f"/workspaces/{ws['id']}/members",
        json={"user_id": 2, "role": "member"},
        headers=_auth_headers(admin_token),
    )

    response = client.delete(f"/workspaces/{ws['id']}", headers=_auth_headers(member_token))
    assert response.status_code == 403


def test_admin_can_delete_workspace(client):
    token = _register_and_login(client, "owner@example.com")
    ws = client.post("/workspaces/", json={"name": "Deletable WS"}, headers=_auth_headers(token)).json()

    response = client.delete(f"/workspaces/{ws['id']}", headers=_auth_headers(token))
    assert response.status_code == 204
