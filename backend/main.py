import os
import sys

# Ensure backend directory is in sys.path regardless of execution working directory
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
from routes import health, demo_data, reconciliation, exceptions, metrics, upload, reviews, ai_assistant
from schemas import RootInfoResponse

# Initialize database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI application
app = FastAPI(
    title="AI Finance Controller — Multi-Source Reconciliation API",
    description="Backend service for multi-source financial reconciliation platform",
    version="1.0.0"
)

# Enable CORS safely for frontend
allowed_origins_env = os.environ.get("ALLOWED_ORIGINS", "")
if allowed_origins_env:
    allowed_origins = [orig.strip() for orig in allowed_origins_env.split(",") if orig.strip()]
else:
    allowed_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/", response_model=RootInfoResponse)
def read_root():
    """Root endpoint returning service identity and status."""
    return {
        "name": "AI Finance Controller",
        "status": "running"
    }

# Register route modules
app.include_router(health.router)
app.include_router(demo_data.router)
app.include_router(reconciliation.router)
app.include_router(exceptions.router)
app.include_router(metrics.router)
app.include_router(upload.router)
app.include_router(reviews.router)
app.include_router(ai_assistant.router)





if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
