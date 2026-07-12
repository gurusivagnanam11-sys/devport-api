from fastapi import FastAPI
app= FastAPI(title="DevPort API Management Paltform")
@app.get("/")
def root():
    return {"message": "Welcome to DevPort API Management Platform"}        