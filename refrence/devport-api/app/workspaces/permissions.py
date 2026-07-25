from enum import Enum


class Role(str, Enum):
    ADMIN = "admin"
    MEMBER = "member"


# Permission matrix: what each role can do
ROLE_PERMISSIONS = {
    Role.ADMIN: {
        "workspace:update",
        "workspace:delete",
        "member:invite",
        "member:remove",
        "apikey:create",
        "apikey:revoke",
        "apikey:rotate",
        "webhook:configure",
        "analytics:view",
    },
    Role.MEMBER: {
        "analytics:view",
        "apikey:use",
    },
}


def role_has_permission(role: str, permission: str) -> bool:
    try:
        role_enum = Role(role)
    except ValueError:
        return False
    return permission in ROLE_PERMISSIONS.get(role_enum, set())
