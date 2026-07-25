def _register_and_login(client, email="keyowner@example.com", password="pass1234"):
    client.post("/auth/register", json={"email": email, "password": password})
    login = client.post("/auth/login", json={"email": email, "password": password})
    return login.json()["access_token"]


def _auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def _setup_workspace(client):
    token = _register_and_login(client)
    ws = client.post("/workspaces/", json={"name": "Key Test WS"}, headers=_auth_headers(token)).json()
    return token, ws["id"]


def test_create_api_key_returns_raw_key_once(client):
    token, ws_id = _setup_workspace(client)

    response = client.post(
        f"/workspaces/{ws_id}/api-keys/",
        json={"name": "Test Key"},
        headers=_auth_headers(token),
    )
    assert response.status_code == 201
    data = response.json()
    assert "raw_key" in data
    assert data["raw_key"].startswith("dp_live_")


def test_list_api_keys_never_returns_raw_key(client):
    token, ws_id = _setup_workspace(client)

    client.post(f"/workspaces/{ws_id}/api-keys/", json={"name": "Key 1"}, headers=_auth_headers(token))
    response = client.get(f"/workspaces/{ws_id}/api-keys/", headers=_auth_headers(token))

    assert response.status_code == 200
    for key in response.json():
        assert "raw_key" not in key
        assert "key_hash" not in key


def test_revoke_api_key(client):
    token, ws_id = _setup_workspace(client)

    created = client.post(
        f"/workspaces/{ws_id}/api-keys/", json={"name": "To Revoke"}, headers=_auth_headers(token)
    ).json()

    response = client.post(
        f"/workspaces/{ws_id}/api-keys/{created['id']}/revoke", headers=_auth_headers(token)
    )
    assert response.status_code == 200
    assert response.json()["is_active"] is False
