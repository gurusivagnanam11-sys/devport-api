import requests
from celery import shared_task

from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.webhooks.models import WebhookDelivery, WebhookEndpoint
from app.webhooks.security import sign_payload
from app.webhooks.service import mark_delivery_result, send_to_dead_letter

MAX_RETRIES = 5
DEFAULT_RETRY_KWARGS = {
    "max_retries": MAX_RETRIES,
    "default_retry_delay": 4,
}


@celery_app.task(bind=True, **DEFAULT_RETRY_KWARGS)
def deliver_webhook(self, delivery_id: int):
    db = SessionLocal()
    try:
        delivery = db.query(WebhookDelivery).filter(WebhookDelivery.id == delivery_id).first()
        if not delivery:
            return

        endpoint = db.query(WebhookEndpoint).filter(WebhookEndpoint.id == delivery.endpoint_id).first()
        if not endpoint or not endpoint.is_active:
            return

        signature = sign_payload(delivery.payload, endpoint.secret)
        headers = {
            "Content-Type": "application/json",
            "X-DevPort-Signature": signature,
        }

        try:
            response = requests.post(endpoint.url, data=delivery.payload, headers=headers, timeout=5)
            success = 200 <= response.status_code < 300
            mark_delivery_result(db, delivery, response.status_code, success)

            if not success:
                raise Exception(f"Non-2xx response: {response.status_code}")

        except Exception as exc:
            mark_delivery_result(db, delivery, None, False)
            try:
                countdown = 2 ** (self.request.retries + 1)
                raise self.retry(exc=exc, countdown=countdown)
            except self.MaxRetriesExceededError:
                send_to_dead_letter(db, delivery_id, reason=str(exc))
    finally:
        db.close()


@celery_app.task
def cleanup_old_deliveries():
    """Delete delivery records older than 30 days to keep the table small."""
    db = SessionLocal()
    try:
        from datetime import datetime, timedelta, timezone

        cutoff = datetime.now(timezone.utc) - timedelta(days=30)
        db.query(WebhookDelivery).filter(WebhookDelivery.created_at < cutoff).delete()
        db.commit()
    finally:
        db.close()
