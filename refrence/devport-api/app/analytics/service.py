from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date
from app.analytics.models import UsageLog


def log_request(db: Session, workspace_id: int, api_key_id: int, endpoint: str,
                 method: str, status_code: int, latency_ms: float):
    entry = UsageLog(
        workspace_id=workspace_id,
        api_key_id=api_key_id,
        endpoint=endpoint,
        method=method,
        status_code=status_code,
        latency_ms=latency_ms,
    )
    db.add(entry)
    db.commit()


def get_total_requests(db: Session, workspace_id: int) -> int:
    return db.query(UsageLog).filter(UsageLog.workspace_id == workspace_id).count()


def get_avg_latency(db: Session, workspace_id: int) -> float:
    result = db.query(func.avg(UsageLog.latency_ms)).filter(
        UsageLog.workspace_id == workspace_id
    ).scalar()
    return round(result, 2) if result else 0.0


def get_top_endpoints(db: Session, workspace_id: int, limit: int = 5):
    rows = (
        db.query(
            UsageLog.endpoint,
            func.count(UsageLog.id).label("request_count"),
            func.avg(UsageLog.latency_ms).label("avg_latency_ms"),
        )
        .filter(UsageLog.workspace_id == workspace_id)
        .group_by(UsageLog.endpoint)
        .order_by(func.count(UsageLog.id).desc())
        .limit(limit)
        .all()
    )
    return [
        {"endpoint": r.endpoint, "request_count": r.request_count, "avg_latency_ms": round(r.avg_latency_ms, 2)}
        for r in rows
    ]


def get_daily_usage(db: Session, workspace_id: int, days: int = 30):
    rows = (
        db.query(
            cast(UsageLog.created_at, Date).label("date"),
            func.count(UsageLog.id).label("request_count"),
        )
        .filter(UsageLog.workspace_id == workspace_id)
        .group_by(cast(UsageLog.created_at, Date))
        .order_by(cast(UsageLog.created_at, Date).desc())
        .limit(days)
        .all()
    )
    return [{"date": str(r.date), "request_count": r.request_count} for r in rows]
