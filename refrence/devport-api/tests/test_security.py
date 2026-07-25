from app.auth.security import hash_password, verify_password, create_access_token, decode_token
from app.api_keys.security import generate_api_key, verify_api_key, hash_api_key


def test_password_hash_is_not_plaintext():
    hashed = hash_password("mypassword123")
    assert hashed != "mypassword123"
    assert hashed.startswith("$2b$")  # bcrypt signature prefix


def test_password_verify_correct_password():
    hashed = hash_password("mypassword123")
    assert verify_password("mypassword123", hashed) is True


def test_password_verify_wrong_password():
    hashed = hash_password("mypassword123")
    assert verify_password("wrongpassword", hashed) is False


def test_access_token_roundtrip():
    token = create_access_token(user_id=42)
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "42"
    assert payload["type"] == "access"


def test_decode_invalid_token_returns_none():
    assert decode_token("not.a.real.token") is None


def test_api_key_generation_is_unique():
    raw1, prefix1, hash1 = generate_api_key()
    raw2, prefix2, hash2 = generate_api_key()
    assert raw1 != raw2
    assert hash1 != hash2


def test_api_key_verify_correct_key():
    raw_key, prefix, key_hash = generate_api_key()
    assert verify_api_key(raw_key, key_hash) is True


def test_api_key_verify_wrong_key_fails():
    raw_key, prefix, key_hash = generate_api_key()
    assert verify_api_key("dp_live_wrongkeyvalue", key_hash) is False


def test_api_key_hash_is_deterministic():
    raw_key, prefix, key_hash = generate_api_key()
    assert hash_api_key(raw_key) == key_hash
