from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.workspaces.dependencies import get_scoped_workspace, require_permission
from app.api_keys import schemas, service
from app.webhooks.service import list_webhooks, create_delivery
from app.webhooks.tasks import deliver_webhook

router = APIRouter(prefix="/workspaces/{workspace_id}/api-keys", tags=["api-keys"])


@router.post("/", response_model=schemas.ApiKeyCreateResponse, status_code=status.HTTP_201_CREATED)
def create_key(
    workspace_id: int,
    payload: schemas.ApiKeyCreate,
    db: Session = Depends(get_db),
    workspace=Depends(get_scoped_workspace),
    membership=Depends(require_permission("apikey:create")),
):
    api_key, raw_key = service.create_api_key(db, workspace_id, payload.name, membership.user_id)

    # Fire "api_key.created" webhook event to any active endpoints for this workspace
    endpoints = list_webhooks(db, workspace_id)
    for endpoint in endpoints:
        if endpoint.is_active:
            delivery = create_delivery(
                db, endpoint.id, event_type="api_key.created",
                payload={
                    "event": "api_key.created",
                    "key_id": api_key.id,
                    "key_prefix": api_key.key_prefix,
                },
            )
            deliver_webhook.delay(delivery.id)

    return schemas.ApiKeyCreateResponse(
        id=api_key.id,
        name=api_key.name,
        key_prefix=api_key.key_prefix,
        raw_key=raw_key,
        created_at=api_key.created_at,
    )


@router.get("/", response_model=list[schemas.ApiKeyResponse])
def list_keys(
    workspace_id: int,
    db: Session = Depends(get_db),
    workspace=Depends(get_scoped_workspace),
):
    return service.list_api_keys(db, workspace_id)


@router.post("/{key_id}/revoke", response_model=schemas.ApiKeyResponse)
def revoke_key(
    workspace_id: int,
    key_id: int,
    db: Session = Depends(get_db),
    workspace=Depends(get_scoped_workspace),
    membership=Depends(require_permission("apikey:revoke")),
):
    api_key = service.get_api_key(db, workspace_id, key_id)
    if not api_key:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found")
    return service.revoke_api_key(db, api_key)


@router.post("/{key_id}/rotate", response_model=schemas.ApiKeyCreateResponse)
def rotate_key(
    workspace_id: int,
    key_id: int,
    db: Session = Depends(get_db),
    workspace=Depends(get_scoped_workspace),
    membership=Depends(require_permission("apikey:rotate")),
):
    api_key = service.get_api_key(db, workspace_id, key_id)
    if not api_key:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found")

    new_key, raw_key = service.rotate_api_key(db, api_key)
    return schemas.ApiKeyCreateResponse(
        id=new_key.id,
        name=new_key.name,
        key_prefix=new_key.key_prefix,
        raw_key=raw_key,
        created_at=new_key.created_at,
    )
