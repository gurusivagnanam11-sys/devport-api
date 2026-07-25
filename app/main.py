from fastapi import FastAPI
from app.auth.router import router as auth_router
from app.workspaces.router import router as workspaces_router

app = FastAPI(title="DevPort API Management Platform")

app.include_router(auth_router)
app.include_router(workspaces_router)


@app.get("/")
def root():
    return {"message": "DevPort is running"}