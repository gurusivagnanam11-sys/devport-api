PLAN_LIMITS = {
    "free": {"limit": 100, "window_seconds": 86400},        # 100/day
    "pro": {"limit": 10000, "window_seconds": 86400},       # 10,000/day
    "enterprise": {"limit": None, "window_seconds": 86400}, # unlimited
}


def get_plan_limit(plan: str) -> dict:
    return PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])
