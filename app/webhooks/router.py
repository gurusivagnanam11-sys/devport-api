from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.webhooks import schemas, service
from app.workspaces.dependencies import get_scoped_workspace, require_permission

router = APIRouter(prefix="/workspaces/{workspace_id}/webhooks", tags=["webhooks"])


@router.post("/", response_model=schemas.WebhookResponse, status_code=status.HTTP_201_CREATED)
def create_webhook(
    workspace_id: int,
    payload: schemas.WebhookCreate,
    db: Session = Depends(get_db),
    workspace=Depends(get_scoped_workspace),
    membership=Depends(require_permission("webhook:configure")),
):
    return service.create_webhook(db, workspace_id, str(payload.url))


@router.get("/", response_model=list[schemas.WebhookResponse])
def list_webhooks(
    workspace_id: int,
    db: Session = Depends(get_db),
    workspace=Depends(get_scoped_workspace),
):
    return service.list_webhooks(db, workspace_id)


@router.delete("/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_webhook(
    workspace_id: int,
    webhook_id: int,
    db: Session = Depends(get_db),
    workspace=Depends(get_scoped_workspace),
    membership=Depends(require_permission("webhook:configure")),
):
    endpoint = service.get_webhook(db, workspace_id, webhook_id)
    if not endpoint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook not found")
    service.deactivate_webhook(db, endpoint)
