from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ApiKeyCreate(BaseModel):
    name: str


class ApiKeyCreateResponse(BaseModel):
    id: int
    name: str
    key_prefix: str
    raw_key: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ApiKeyResponse(BaseModel):
    id: int
    name: str
    key_prefix: str
    is_active: bool
    created_at: datetime
    revoked_at: datetime | None
    last_used_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
