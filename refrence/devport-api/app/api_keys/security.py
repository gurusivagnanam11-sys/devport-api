import secrets
import hashlib

KEY_PREFIX_LENGTH = 12


def generate_api_key() -> tuple[str, str, str]:
    """
    Returns (raw_key, key_prefix, key_hash).
    raw_key is shown to the user ONCE and never stored.
    """
    raw_secret = secrets.token_hex(32)  # 64 hex chars, CSPRNG - cryptographically secure
    raw_key = f"dp_live_{raw_secret}"

    key_prefix = raw_key[:KEY_PREFIX_LENGTH]
    key_hash = hash_api_key(raw_key)

    return raw_key, key_prefix, key_hash


def hash_api_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode()).hexdigest()


def verify_api_key(raw_key: str, stored_hash: str) -> bool:
    computed_hash = hash_api_key(raw_key)
    return secrets.compare_digest(computed_hash, stored_hash)
