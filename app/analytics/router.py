from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.analytics import schemas, service
from app.core.database import get_db
from app.workspaces.dependencies import get_scoped_workspace

router = APIRouter(prefix="/workspaces/{workspace_id}/analytics", tags=["analytics"])


@router.get("/", response_model=schemas.WorkspaceAnalytics)
def get_analytics(
    workspace_id: int,
    db: Session = Depends(get_db),
    workspace=Depends(get_scoped_workspace),
):
    return schemas.WorkspaceAnalytics(
        total_requests=service.get_total_requests(db, workspace_id),
        avg_latency_ms=service.get_avg_latency(db, workspace_id),
        top_endpoints=service.get_top_endpoints(db, workspace_id),
        daily_usage=service.get_daily_usage(db, workspace_id),
    )
