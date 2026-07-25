from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.workspaces import service
from app.workspaces.models import Workspace
from app.workspaces.permissions import role_has_permission


def get_workspace_or_404(workspace_id: int, db: Session = Depends(get_db)):
    workspace = service.get_workspace(db, workspace_id)
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    return workspace


def require_membership(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    membership = service.get_membership(db, workspace_id, current_user.id)
    if not membership:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of this workspace")
    return membership


def get_scoped_workspace(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Workspace:
    """
    Returns the workspace ONLY if it exists AND the current user is a member.
    Combines 404 (not found) and 403 (not a member) into one safe check —
    never leaks whether a workspace exists to a non-member (IDOR prevention).
    """
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    membership = service.get_membership(db, workspace_id, current_user.id)

    if not workspace or not membership:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")

    return workspace


def require_permission(permission: str):
    def dependency(
        workspace_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        membership = service.get_membership(db, workspace_id, current_user.id)
        if not membership:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of this workspace")
        if not role_has_permission(membership.role, permission):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Missing permission: {permission}")
        return membership
    return dependency
