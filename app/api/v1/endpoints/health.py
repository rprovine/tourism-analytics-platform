from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import get_db
from app.core.redis_client import redis_client
from app.integrations.hubspot_client import hubspot_client
import asyncio

router = APIRouter()


@router.get("/")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "service": "Tourism Analytics Platform",
        "version": "1.0.0"
    }


@router.get("/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """Detailed health check including all dependencies"""
    health_status = {
        "status": "healthy",
        "checks": {}
    }
    
    # Database check
    try:
        await db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = {"status": "healthy"}
    except Exception as e:
        health_status["checks"]["database"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "unhealthy"
    
    # Redis check
    try:
        await redis_client.set("health_check", "ok", expire=60)
        test_value = await redis_client.get("health_check")
        if test_value == "ok":
            health_status["checks"]["redis"] = {"status": "healthy"}
        else:
            health_status["checks"]["redis"] = {"status": "unhealthy", "error": "Test value mismatch"}
            health_status["status"] = "unhealthy"
    except Exception as e:
        health_status["checks"]["redis"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "unhealthy"
    
    # HubSpot check (optional)
    try:
        hubspot_test = await hubspot_client.test_connection()
        if hubspot_test.get("status") == "success":
            health_status["checks"]["hubspot"] = {"status": "healthy"}
        else:
            health_status["checks"]["hubspot"] = {"status": "unhealthy", "error": hubspot_test.get("message")}
    except Exception as e:
        health_status["checks"]["hubspot"] = {"status": "unhealthy", "error": str(e)}
    
    return health_status