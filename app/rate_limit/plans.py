PLAN_LIMITS = {
    "free": {"limit": 100, "window_seconds": 86400},
    "pro": {"limit": 10000, "window_seconds": 86400},
    "enterprise": {"limit": None, "window_seconds": 86400},
}


def get_plan_limit(plan: str) -> dict:
    return PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])
