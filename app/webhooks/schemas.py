from datetime import datetime

from pydantic import BaseModel, ConfigDict, HttpUrl


class WebhookCreate(BaseModel):
    url: HttpUrl


class WebhookResponse(BaseModel):
    id: int
    url: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DeliveryResponse(BaseModel):
    id: int
    event_type: str
    status_code: int | None
    success: bool
    attempt_count: int
    created_at: datetime
    delivered_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
