from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.api_keys.models import ApiKey
from app.api_keys.security import generate_api_key, hash_api_key


def create_api_key(db: Session, workspace_id: int, name: str, created_by_user_id: int):
    raw_key, key_prefix, key_hash = generate_api_key()

    api_key = ApiKey(
        workspace_id=workspace_id,
        name=name,
        key_prefix=key_prefix,
        key_hash=key_hash,
        created_by_user_id=created_by_user_id,
    )
    db.add(api_key)
    db.commit()
    db.refresh(api_key)

    # raw_key is returned ONLY here, attached temporarily - never persisted
    return api_key, raw_key


def list_api_keys(db: Session, workspace_id: int):
    return db.query(ApiKey).filter(ApiKey.workspace_id == workspace_id).all()


def get_api_key(db: Session, workspace_id: int, key_id: int):
    return db.query(ApiKey).filter(
        ApiKey.id == key_id,
        ApiKey.workspace_id == workspace_id,
    ).first()


def revoke_api_key(db: Session, api_key: ApiKey):
    api_key.is_active = False
    api_key.revoked_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(api_key)
    return api_key


def rotate_api_key(db: Session, api_key: ApiKey):
    """Revoke the old key, issue a brand new one under the same name/workspace."""
    revoke_api_key(db, api_key)

    new_key, raw_key = create_api_key(
        db, api_key.workspace_id, api_key.name, api_key.created_by_user_id
    )
    return new_key, raw_key


def find_active_key_by_raw(db: Session, raw_key: str) -> ApiKey | None:
    """Used by the gateway/middleware to validate incoming API key headers."""
    key_hash = hash_api_key(raw_key)
    return db.query(ApiKey).filter(
        ApiKey.key_hash == key_hash,
        ApiKey.is_active == True,  # noqa: E712
    ).first()
