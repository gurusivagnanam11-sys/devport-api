from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.auth.router import router as auth_router
from app.workspaces.router import router as workspaces_router
from app.api_keys.router import router as api_keys_router
from app.analytics.router import router as analytics_router
from app.webhooks.router import router as webhooks_router
from app.gateway.router import router as gateway_router

logger = logging.getLogger("devport")

app = FastAPI(title="DevPort API Management Platform")

# CORS - replace allow_origins with your real frontend origin(s) before production.
# Never use ["*"] combined with allow_credentials=True.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(workspaces_router)
app.include_router(api_keys_router)
app.include_router(analytics_router)
app.include_router(webhooks_router)
app.include_router(gateway_router)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception on %s %s", request.method, request.url)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


@app.get("/")
def root():
    return {"message": "DevPort is running"}
