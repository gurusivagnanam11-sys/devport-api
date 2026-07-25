from app.core.redis_client import redis_client

# Atomic fixed-window rate limiter.
# KEYS[1] = redis key for this api key's current window
# ARGV[1] = limit (max requests allowed in window)
# ARGV[2] = window size in seconds
#
# Returns: {allowed (1/0), current_count, ttl_remaining}
RATE_LIMIT_LUA = """
local current = redis.call("INCR", KEYS[1])
if current == 1 then
    redis.call("EXPIRE", KEYS[1], ARGV[2])
end
local ttl = redis.call("TTL", KEYS[1])
local limit = tonumber(ARGV[1])

if limit == nil then
    return {1, current, ttl}
end

if current > limit then
    return {0, current, ttl}
else
    return {1, current, ttl}
end
"""

_rate_limit_script = redis_client.register_script(RATE_LIMIT_LUA)


class RateLimitResult:
    def __init__(self, allowed: bool, current: int, retry_after: int):
        self.allowed = allowed
        self.current = current
        self.retry_after = retry_after


def check_rate_limit(key_id: int, limit: int | None, window_seconds: int) -> RateLimitResult:
    redis_key = f"ratelimit:apikey:{key_id}"

    if limit is None:
        return RateLimitResult(allowed=True, current=0, retry_after=0)

    try:
        result = _rate_limit_script(keys=[redis_key], args=[limit, window_seconds])
        current, ttl = result[1], result[2]
        allowed = result[0] == 1
        return RateLimitResult(allowed=allowed, current=current, retry_after=ttl)
    except Exception:
        # FAIL OPEN: if Redis is unreachable, we allow requests rather than blocking
        # all traffic platform-wide. Tradeoff: a Redis outage temporarily disables
        # rate limiting rather than causing a full outage. Revisit if abuse risk
        # during Redis downtime becomes a real concern.
        return RateLimitResult(allowed=True, current=0, retry_after=0)
