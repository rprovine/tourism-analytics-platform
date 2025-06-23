from fastapi import APIRouter
from app.api.v1.endpoints import reviews, forecasting, chat, dashboard, leads, health, landing

api_router = APIRouter()

api_router.include_router(landing.router, prefix="", tags=["landing"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
api_router.include_router(forecasting.router, prefix="/forecasting", tags=["forecasting"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(leads.router, prefix="/leads", tags=["leads"])