from fastapi import FastAPI
from api.webhooks import router as webhooks_router

app = FastAPI(title="Antigravity Engine API")

app.include_router(webhooks_router, prefix="/webhooks", tags=["Webhooks"])

@app.get("/")
def read_root():
    return {"message": "Antigravity Engine is running!"}
