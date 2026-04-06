"""
MoodTunes API — FastAPI application entry point.

Run:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Docs:
    http://localhost:8000/docs    (Swagger UI)
    http://localhost:8000/redoc   (ReDoc)
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database import engine, Base
from app.auth.router import router as auth_router
from app.mood.router import router as mood_router
from app.mood.websocket import ws_router
from app.music.router import router as music_router
from app.music.deezer_router import router as deezer_router
from app.playlists.router import router as playlist_router
from app.mood.detector import MoodDetector

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle hooks."""
    # ── Startup ──
    # Create tables (use Alembic migrations in production)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables ready")

    # Load ML model
    detector = MoodDetector.get_instance()
    detector.load()

    yield

    # ── Shutdown ──
    await engine.dispose()
    print("Database connections closed")


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered emotion-based music recommendation platform",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ──
api_prefix = settings.API_V1_PREFIX

app.include_router(auth_router, prefix=api_prefix)
app.include_router(mood_router, prefix=api_prefix)
app.include_router(music_router, prefix=api_prefix)
app.include_router(deezer_router, prefix=api_prefix)
app.include_router(playlist_router, prefix=api_prefix)
app.include_router(ws_router)  # WebSocket at /ws/mood


# ── Health Check ──
@app.get("/health")
async def health_check():
    detector = MoodDetector.get_instance()
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "model_loaded": detector.model is not None,
    }


# ── Global Exception Handler ──
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )