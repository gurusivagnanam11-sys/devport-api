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

    # User B (not a member) tries to access User A's workspace
    response = client.get(f"/workspaces/{ws['id']}", headers=_auth_headers(token_b))
    assert response.status_code == 404  # NOT 403 - see Module 10 (IDOR prevention)


def test_admin_can_delete_workspace(client):
    token = _register_and_login(client, "owner@example.com")
    ws = client.post("/workspaces/", json={"name": "Deletable WS"}, headers=_auth_headers(token)).json()

    response = client.delete(f"/workspaces/{ws['id']}", headers=_auth_headers(token))
    assert response.status_code == 204
