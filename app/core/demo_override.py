"""
Demo database dependency override for production deployment without PostgreSQL
"""
import os
from fastapi import HTTPException
from app.core.demo_database import demo_db

async def get_demo_db():
    """Override database dependency to use demo data"""
    return demo_db

def should_use_demo_db() -> bool:
    """Check if we should use demo database instead of real database"""
    return os.getenv("DATABASE_URL") is None or os.getenv("USE_DEMO_DATA") == "true"