from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.workspaces import schemas, service
from app.workspaces.models import WorkspaceMember
from app.workspaces.dependencies import require_membership, require_permission, get_scoped_workspace

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.post("/", response_model=schemas.WorkspaceResponse, status_code=status.HTTP_201_CREATED)
def create_workspace(
    payload: schemas.WorkspaceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.create_workspace(db, payload.name, current_user.id)


@router.get("/", response_model=list[schemas.WorkspaceResponse])
def list_my_workspaces(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.get_user_workspaces(db, current_user.id)


@router.get("/{workspace_id}", response_model=schemas.WorkspaceResponse)
def get_workspace(
    workspace_id: int,
    workspace=Depends(get_scoped_workspace),
):
    return workspace


@router.put("/{workspace_id}", response_model=schemas.WorkspaceResponse)
def update_workspace(
    workspace_id: int,
    payload: schemas.WorkspaceUpdate,
    db: Session = Depends(get_db),
    workspace=Depends(get_scoped_workspace),
    membership=Depends(require_permission("workspace:update")),
):
    return service.update_workspace(db, workspace, payload.name)


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workspace(
    workspace_id: int,
    db: Session = Depends(get_db),
    workspace=Depends(get_scoped_workspace),
    membership=Depends(require_permission("workspace:delete")),
):
    service.delete_workspace(db, workspace)


@router.post("/{workspace_id}/members", response_model=schemas.MemberResponse, status_code=status.HTTP_201_CREATED)
def invite_member(
    workspace_id: int,
    payload: schemas.MemberInvite,
    db: Session = Depends(get_db),
    workspace=Depends(get_scoped_workspace),
    membership=Depends(require_permission("member:invite")),
):
    try:
        return service.add_member(db, workspace_id, payload.user_id, payload.role)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{workspace_id}/members", response_model=list[schemas.MemberResponse])
def get_members(
    workspace_id: int,
    db: Session = Depends(get_db),
    workspace=Depends(get_scoped_workspace),
):
    return service.list_members(db, workspace_id)


@router.delete("/{workspace_id}/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(
    workspace_id: int,
    member_id: int,
    db: Session = Depends(get_db),
    workspace=Depends(get_scoped_workspace),
    membership=Depends(require_permission("member:remove")),
):
    target = db.query(WorkspaceMember).filter(
        WorkspaceMember.id == member_id,
        WorkspaceMember.workspace_id == workspace_id,
    ).first()
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    service.remove_member(db, target)
