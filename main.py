from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router
from app.core.logger import logging

app = FastAPI(title="AI Data Agent")

# Log app startup
logging.info("Starting FastAPI app...")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    logging.info("Serving index.html")
    return FileResponse("static/index.html")

# Include API routes
app.include_router(api_router)
