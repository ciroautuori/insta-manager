from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
import redis
from typing import Dict, Any

from app.core.database import get_db
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Instagram Manager API",
        "version": "1.0.0"
    }


@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Detailed health check with dependency status."""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Instagram Manager API",
        "version": "1.0.0",
        "checks": {}
    }
    
    overall_healthy = True
    
    # Database health check
    try:
        db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = {
            "status": "healthy",
            "message": "Database connection successful"
        }
        logger.debug("Database health check passed")
    except Exception as e:
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}"
        }
        overall_healthy = False
        logger.error(f"Database health check failed: {str(e)}")
    
    # Redis health check
    try:
        redis_client = redis.from_url(settings.REDIS_URL)
        redis_client.ping()
        health_status["checks"]["redis"] = {
            "status": "healthy",
            "message": "Redis connection successful"
        }
        logger.debug("Redis health check passed")
    except Exception as e:
        health_status["checks"]["redis"] = {
            "status": "unhealthy",
            "message": f"Redis connection failed: {str(e)}"
        }
        overall_healthy = False
        logger.error(f"Redis health check failed: {str(e)}")
    
    # Celery health check
    try:
        from app.workers.celery_app import celery_app
        inspect = celery_app.control.inspect()
        stats = inspect.stats()
        
        if stats:
            health_status["checks"]["celery"] = {
                "status": "healthy",
                "message": f"Celery workers active: {len(stats)}",
                "workers": list(stats.keys())
            }
            logger.debug(f"Celery health check passed: {len(stats)} workers active")
        else:
            health_status["checks"]["celery"] = {
                "status": "unhealthy",
                "message": "No Celery workers available"
            }
            overall_healthy = False
            logger.warning("Celery health check failed: no workers available")
            
    except Exception as e:
        health_status["checks"]["celery"] = {
            "status": "unhealthy",
            "message": f"Celery check failed: {str(e)}"
        }
        overall_healthy = False
        logger.error(f"Celery health check failed: {str(e)}")
    
    # Instagram API connectivity check
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://graph.instagram.com/me",
                params={"access_token": "test", "fields": "id"},
                timeout=5.0
            )
            # We expect this to fail with 400 (invalid token), not connection error
            if response.status_code in [400, 401]:
                health_status["checks"]["instagram_api"] = {
                    "status": "healthy",
                    "message": "Instagram API is reachable"
                }
                logger.debug("Instagram API health check passed")
            else:
                health_status["checks"]["instagram_api"] = {
                    "status": "degraded",
                    "message": f"Instagram API returned unexpected status: {response.status_code}"
                }
                logger.warning(f"Instagram API health check degraded: status {response.status_code}")
                
    except Exception as e:
        health_status["checks"]["instagram_api"] = {
            "status": "unhealthy",
            "message": f"Instagram API unreachable: {str(e)}"
        }
        overall_healthy = False
        logger.error(f"Instagram API health check failed: {str(e)}")
    
    # Update overall status
    if not overall_healthy:
        health_status["status"] = "unhealthy"
    
    return health_status


@router.get("/health/readiness")
async def readiness_check(db: Session = Depends(get_db)):
    """Kubernetes readiness probe endpoint."""
    try:
        # Check critical dependencies
        db.execute(text("SELECT 1"))
        
        redis_client = redis.from_url(settings.REDIS_URL)
        redis_client.ping()
        
        return {"status": "ready"}
        
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return {"status": "not ready", "error": str(e)}, status.HTTP_503_SERVICE_UNAVAILABLE


@router.get("/health/liveness")
async def liveness_check():
    """Kubernetes liveness probe endpoint."""
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}


@router.get("/metrics")
async def metrics_endpoint(db: Session = Depends(get_db)):
    """Basic metrics endpoint for monitoring."""
    try:
        # Database connection count
        db_connections = db.execute(text(
            "SELECT count(*) FROM pg_stat_activity WHERE state = 'active'"
        )).scalar()
        
        # Redis info
        redis_client = redis.from_url(settings.REDIS_URL)
        redis_info = redis_client.info()
        
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "database": {
                "active_connections": db_connections,
                "status": "healthy"
            },
            "redis": {
                "connected_clients": redis_info.get("connected_clients", 0),
                "used_memory": redis_info.get("used_memory", 0),
                "status": "healthy"
            },
            "application": {
                "uptime_seconds": redis_info.get("uptime_in_seconds", 0),
                "status": "healthy"
            }
        }
        
        return metrics
        
    except Exception as e:
        logger.error(f"Metrics collection failed: {str(e)}")
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "error",
            "error": str(e)
        }, status.HTTP_500_INTERNAL_SERVER_ERROR
