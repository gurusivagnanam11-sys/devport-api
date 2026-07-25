from pydantic import BaseModel, ConfigDict
from datetime import datetime


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


class MemberResponse(BaseModel):
    id: int
    user_id: int
    workspace_id: int
    role: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)