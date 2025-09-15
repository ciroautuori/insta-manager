from fastapi import APIRouter
from app.api.endpoints import auth, admin, instagram, posts, media, scheduled, analytics, dashboard

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(instagram.router, prefix="/instagram", tags=["instagram"])
api_router.include_router(posts.router, prefix="/posts", tags=["posts"])
api_router.include_router(media.router, prefix="/media", tags=["media"])
api_router.include_router(scheduled.router, prefix="/scheduled", tags=["scheduled-posts"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
