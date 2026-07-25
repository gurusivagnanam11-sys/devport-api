from fastapi import FastAPI
from app.analytics.router import router as analytics_router
from app.api_keys.router import router as api_keys_router
from app.auth.router import router as auth_router
from app.gateway.router import router as gateway_router
from app.webhooks.router import router as webhooks_router
from app.workspaces.router import router as workspaces_router

app = FastAPI(title="DevPort API Management Platform")

app.include_router(auth_router)
app.include_router(workspaces_router)
app.include_router(api_keys_router)
app.include_router(analytics_router)
app.include_router(gateway_router)
app.include_router(webhooks_router)


@app.get("/")
def root():
    return {"message": "DevPort is running"}