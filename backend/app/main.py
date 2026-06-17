import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import init_db
from app.api.auth import router as auth_router
from app.api.lyrics import router as lyrics_router
from app.api.music import router as music_router
from app.api.files import router as files_router
from app.api.albums import router as albums_router
from app.api.arrangement import router as arrangement_router
from app.api.vocal import router as vocal_router
from app.api.mastering import router as mastering_router
from app.api.cover import router as cover_router

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AIMBP backend...")
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
    yield
    logger.info("Shutting down AIMBP backend...")


app = FastAPI(
    title="AI Music Business Platform API",
    description="Backend API for AIMBP - AI-powered music creation and distribution",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "data": None,
            "error": "Internal server error",
        },
    )


# Health check
@app.get("/health", tags=["health"])
async def health_check():
    return {
        "success": True,
        "data": {
            "status": "ok",
            "version": "1.0.0",
            "env": settings.APP_ENV,
        },
        "error": None,
    }


# API v1 prefix
API_PREFIX = "/api/v1"

app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(lyrics_router, prefix=API_PREFIX)
app.include_router(music_router, prefix=API_PREFIX)
app.include_router(files_router, prefix=API_PREFIX)
app.include_router(albums_router, prefix=API_PREFIX)
app.include_router(arrangement_router, prefix=API_PREFIX)
app.include_router(vocal_router, prefix=API_PREFIX)
app.include_router(mastering_router, prefix=API_PREFIX)
app.include_router(cover_router, prefix=API_PREFIX)


@app.get("/", tags=["root"])
async def root():
    return {
        "success": True,
        "data": {
            "message": "AIMBP API is running",
            "docs": "/docs",
            "health": "/health",
        },
        "error": None,
    }
