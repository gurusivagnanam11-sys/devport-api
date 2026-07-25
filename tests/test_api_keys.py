from app.api_keys.security import generate_api_key, hash_api_key, verify_api_key


def test_generate_api_key_returns_prefixed_raw_key_and_hash():
    raw_key, key_prefix, key_hash = generate_api_key()

    assert raw_key.startswith("dp_live_")
    assert key_prefix == raw_key[:12]
    assert key_hash == hash_api_key(raw_key)
    assert len(key_hash) == 64


def test_verify_api_key_matches_and_rejects_wrong_values():
    raw_key, _, key_hash = generate_api_key()

    assert verify_api_key(raw_key, key_hash) is True
    assert verify_api_key("dp_live_not_the_real_key", key_hash) is False
