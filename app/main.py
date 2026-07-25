import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.analytics.router import router as analytics_router
from app.api_keys.router import router as api_keys_router
from app.auth.router import router as auth_router
from app.gateway.router import router as gateway_router
from app.webhooks.router import router as webhooks_router
from app.workspaces.router import router as workspaces_router

logger = logging.getLogger("devport")

app = FastAPI(title="DevPort API Management Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(workspaces_router)
app.include_router(api_keys_router)
app.include_router(analytics_router)
app.include_router(gateway_router)
app.include_router(webhooks_router)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception on %s %s", request.method, request.url)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/")
def root():
    return {"message": "DevPort is running"}