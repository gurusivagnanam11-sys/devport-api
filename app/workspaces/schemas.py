from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime
from app.workspaces.permissions import Role


class WorkspaceCreate(BaseModel):
    name: str


class WorkspaceUpdate(BaseModel):
    name: str


class WorkspaceResponse(BaseModel):
    id: int
    name: str
    owner_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MemberInvite(BaseModel):
    user_id: int
    role: str = "member"

    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        if v not in [r.value for r in Role]:
            raise ValueError(f"Invalid role: {v}")
        return v


class MemberResponse(BaseModel):
    id: int
    user_id: int
    workspace_id: int
    role: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)