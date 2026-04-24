from fastapi import FastAPI
from contextlib import asynccontextmanager
from backend.db.session import init_db
from backend.api.auth import router as auth_router
from backend.api.predict import router as predict_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(title="ChurnSaaS API", lifespan=lifespan)

app.include_router(auth_router)
app.include_router(predict_router)

@app.get("/health")
async def health():
    return {"status": "ok"}
