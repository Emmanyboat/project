from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, vehicles, violations, scans, analytics

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(vehicles.router, prefix="/vehicles", tags=["vehicles"])
api_router.include_router(violations.router, prefix="/violations", tags=["violations"])
api_router.include_router(scans.router, prefix="/scans", tags=["scans"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])