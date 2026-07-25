from sqlalchemy.orm import Session
from app.workspaces.models import Workspace, WorkspaceMember


def create_workspace(db: Session, name: str, owner_id: int) -> Workspace:
    workspace = Workspace(name=name, owner_id=owner_id)
    db.add(workspace)
    db.commit()
    db.refresh(workspace)

    # Owner is automatically an admin member
    membership = WorkspaceMember(workspace_id=workspace.id, user_id=owner_id, role="admin")
    db.add(membership)
    db.commit()

    return workspace


def get_workspace(db: Session, workspace_id: int) -> Workspace | None:
    return db.query(Workspace).filter(Workspace.id == workspace_id).first()


def get_user_workspaces(db: Session, user_id: int) -> list[Workspace]:
    return (
        db.query(Workspace)
        .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
        .filter(WorkspaceMember.user_id == user_id)
        .all()
    )


def update_workspace(db: Session, workspace: Workspace, name: str) -> Workspace:
    workspace.name = name
    db.commit()
    db.refresh(workspace)
    return workspace


def delete_workspace(db: Session, workspace: Workspace) -> None:
    db.delete(workspace)
    db.commit()


def get_membership(db: Session, workspace_id: int, user_id: int) -> WorkspaceMember | None:
    return (
        db.query(WorkspaceMember)
        .filter(WorkspaceMember.workspace_id == workspace_id, WorkspaceMember.user_id == user_id)
        .first()
    )


def add_member(db: Session, workspace_id: int, user_id: int, role: str) -> WorkspaceMember:
    existing = get_membership(db, workspace_id, user_id)
    if existing:
        raise ValueError("User is already a member of this workspace")

    membership = WorkspaceMember(workspace_id=workspace_id, user_id=user_id, role=role)
    db.add(membership)
    db.commit()
    db.refresh(membership)
    return membership


def remove_member(db: Session, membership: WorkspaceMember) -> None:
    db.delete(membership)
    db.commit()


def list_members(db: Session, workspace_id: int) -> list[WorkspaceMember]:
    return db.query(WorkspaceMember).filter(WorkspaceMember.workspace_id == workspace_id).all()
