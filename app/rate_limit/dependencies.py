from fastapi import HTTPException, status

from app.rate_limit.limiter import check_rate_limit
from app.rate_limit.plans import get_plan_limit


def enforce_rate_limit(api_key_id: int, plan: str = "free"):
    plan_config = get_plan_limit(plan)
    result = check_rate_limit(api_key_id, plan_config["limit"], plan_config["window_seconds"])

    if not result.allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
            headers={"Retry-After": str(result.retry_after)},
        )
    return result
