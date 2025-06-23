from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from app.core.config import settings

# Only create database engine if DATABASE_URL exists
if os.getenv("DATABASE_URL") and os.getenv("USE_DEMO_DATA") != "true":
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        future=True
    )
    
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
else:
    engine = None
    AsyncSessionLocal = None

Base = declarative_base()


async def get_db():
    """Database dependency - uses demo data if no DATABASE_URL"""
    from app.core.demo_database import demo_db
    
    if os.getenv("DATABASE_URL") is None or os.getenv("USE_DEMO_DATA") == "true":
        # Return demo database instead
        yield demo_db
    else:
        async with AsyncSessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()