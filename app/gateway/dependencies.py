from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.api_keys.service import find_active_key_by_raw
from app.core.database import get_db
from app.rate_limit.dependencies import enforce_rate_limit


def validate_api_key(
    x_api_key: str = Header(...),
    db: Session = Depends(get_db),
):
    api_key = find_active_key_by_raw(db, x_api_key)
    if not api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or inactive API key")

    enforce_rate_limit(api_key.id, plan="free")

    return api_key
