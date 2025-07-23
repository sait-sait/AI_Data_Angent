from fastapi import FastAPI
from app.api.routes import router as api_router
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="AI Data Agent")
app.include_router(api_router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


