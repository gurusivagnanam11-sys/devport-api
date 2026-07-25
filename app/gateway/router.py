from fastapi import APIRouter, Depends

from app.gateway.dependencies import validate_api_key

router = APIRouter(prefix="/v1", tags=["protected-api"])


@router.get("/weather")
def get_weather(api_key=Depends(validate_api_key)):
    return {"city": "Chennai", "temp": 34, "condition": "Sunny"}
