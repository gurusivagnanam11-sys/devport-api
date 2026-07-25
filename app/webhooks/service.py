import json
import secrets
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.webhooks.models import DeadLetterJob, WebhookDelivery, WebhookEndpoint


def create_webhook(db: Session, workspace_id: int, url: str) -> WebhookEndpoint:
    endpoint = WebhookEndpoint(
        workspace_id=workspace_id,
        url=url,
        secret=secrets.token_hex(32),
    )
    db.add(endpoint)
    db.commit()
    db.refresh(endpoint)
    return endpoint


def list_webhooks(db: Session, workspace_id: int):
    return db.query(WebhookEndpoint).filter(WebhookEndpoint.workspace_id == workspace_id).all()


def get_webhook(db: Session, workspace_id: int, webhook_id: int):
    return db.query(WebhookEndpoint).filter(
        WebhookEndpoint.id == webhook_id,
        WebhookEndpoint.workspace_id == workspace_id,
    ).first()


def deactivate_webhook(db: Session, endpoint: WebhookEndpoint):
    endpoint.is_active = False
    db.commit()


def create_delivery(db: Session, endpoint_id: int, event_type: str, payload: dict) -> WebhookDelivery:
    delivery = WebhookDelivery(
        endpoint_id=endpoint_id,
        event_type=event_type,
        payload=json.dumps(payload),
    )
    db.add(delivery)
    db.commit()
    db.refresh(delivery)
    return delivery


def mark_delivery_result(db: Session, delivery: WebhookDelivery, status_code: int | None, success: bool):
    delivery.status_code = status_code
    delivery.success = success
    delivery.attempt_count += 1
    if success:
        delivery.delivered_at = datetime.now(timezone.utc)
    db.commit()


def send_to_dead_letter(db: Session, delivery_id: int, reason: str):
    entry = DeadLetterJob(delivery_id=delivery_id, reason=reason)
    db.add(entry)
    db.commit()
