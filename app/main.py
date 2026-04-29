from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="AI Dev Assistant", version="0.1.0")
app.include_router(router)

@app.get("/health")
async def health():
    return {"status": "ok"}