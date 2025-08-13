from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import load_settings

# Load settings from .env
settings = load_settings()

# Create FastAPI app instance
app = FastAPI(
    title="Echoverse Backend",
    description="Backend API for Echoverse",
    version="1.0.0"
)

# Apply CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins if settings.cors_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def read_root():
    return {
        "message": "Hello from Echoverse Backend!",
        "log_level": settings.log_level,
        "cors_origins": settings.cors_origins
    }

# Health check
@app.get("/health")
async def health_check():
    return {"status": "ok"}
