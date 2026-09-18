from fastapi import APIRouter

from app.api.v1.analytics import router as analytics_router
from app.api.v1.chat import router as chat_router
from app.api.v1.integrations import router as integrations_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(chat_router, prefix="/chat", tags=["chat"])
api_router.include_router(integrations_router, prefix="/integrations", tags=["integrations"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
