from enum import Enum

from fastapi import Depends, HTTPException, status

from app.core.security import get_current_user


class Role(str, Enum):
    CAMPAIGN_MANAGER = "CAMPAIGN_MANAGER"
    RETAIL_MANAGER = "RETAIL_MANAGER"


class Permission(str, Enum):
    CREATE_CAMPAIGN = "CREATE_CAMPAIGN"
    VIEW_CAMPAIGN = "VIEW_CAMPAIGN"
    MANAGE_CAMPAIGN = "MANAGE_CAMPAIGN"
    VIEW_ANALYTICS = "VIEW_ANALYTICS"
    VIEW_DASHBOARD = "VIEW_DASHBOARD"
    MANAGE_SETTINGS = "MANAGE_SETTINGS"
    VIEW_REVENUE = "VIEW_REVENUE"
    VIEW_DEALER_PERFORMANCE = "VIEW_DEALER_PERFORMANCE"
    VIEW_ROI = "VIEW_ROI"


ROLE_PERMISSIONS: dict[Role, list[Permission]] = {
    Role.CAMPAIGN_MANAGER: [
        Permission.CREATE_CAMPAIGN,
        Permission.VIEW_CAMPAIGN,
        Permission.MANAGE_CAMPAIGN,
        Permission.VIEW_ANALYTICS,
        Permission.VIEW_DASHBOARD,
        Permission.MANAGE_SETTINGS,
        Permission.VIEW_ROI,
    ],
    Role.RETAIL_MANAGER: [
        Permission.VIEW_CAMPAIGN,
        Permission.VIEW_ANALYTICS,
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_REVENUE,
        Permission.VIEW_DEALER_PERFORMANCE,
        Permission.VIEW_ROI,
    ],
}


def require_role(roles: list[str]):
    async def role_checker(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role")
        if user_role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role privileges",
            )
        return current_user

    return role_checker


def require_permission(permission: Permission):
    async def permission_checker(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role")
        try:
            role_enum = Role(user_role)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid role",
            )
        if permission not in ROLE_PERMISSIONS.get(role_enum, []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission.value}' not granted for role '{user_role}'",
            )
        return current_user

    return permission_checker
