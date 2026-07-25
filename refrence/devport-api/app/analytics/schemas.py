from pydantic import BaseModel


class EndpointStat(BaseModel):
    endpoint: str
    request_count: int
    avg_latency_ms: float


class DailyUsage(BaseModel):
    date: str
    request_count: int


class WorkspaceAnalytics(BaseModel):
    total_requests: int
    avg_latency_ms: float
    top_endpoints: list[EndpointStat]
    daily_usage: list[DailyUsage]
