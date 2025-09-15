from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import time
from loguru import logger

from app.core.config import settings
from app.core.database import engine
from app.api.routes import api_router
from app.core.security import limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

# Crea le tabelle del database
from app.models import Base
Base.metadata.create_all(bind=engine)

# Inizializza l'applicazione FastAPI
app = FastAPI(
    title="Instagram Manager API",
    description="API per la gestione centralizzata di account Instagram",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware per logging delle richieste
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    # Log non sensibile: presenza header Authorization e Origin
    auth_header = "present" if request.headers.get("authorization") else "absent"
    origin = request.headers.get("origin", "-")

    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.4f}s - "
        f"Auth: {auth_header} - Origin: {origin}"
    )
    
    return response

# Mount per file media statici
if not os.path.exists(settings.MEDIA_STORAGE_PATH):
    os.makedirs(settings.MEDIA_STORAGE_PATH, exist_ok=True)

app.mount("/media", StaticFiles(directory=settings.MEDIA_STORAGE_PATH), name="media")

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "Instagram Manager API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "environment": settings.ENVIRONMENT}
