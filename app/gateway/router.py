import time

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.analytics.service import log_request
from app.core.database import get_db
from app.gateway.dependencies import validate_api_key

router = APIRouter(prefix="/v1", tags=["protected-api"])


@router.get("/weather")
def get_weather(api_key=Depends(validate_api_key), db: Session = Depends(get_db)):
    start = time.perf_counter()
    response = {"city": "Chennai", "temp": 34, "condition": "Sunny"}
    latency_ms = (time.perf_counter() - start) * 1000

    log_request(
        db,
        api_key.workspace_id,
        api_key.id,
        endpoint="/v1/weather",
        method="GET",
        status_code=200,
        latency_ms=latency_ms,
    )
    return response
