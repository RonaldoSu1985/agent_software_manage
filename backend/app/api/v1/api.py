from fastapi import APIRouter
from app.api.v1.endpoints import auth, inventory, business, common, rbac

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
api_router.include_router(business.router, prefix="/business", tags=["business"])
api_router.include_router(common.router, prefix="/common", tags=["common"])
api_router.include_router(rbac.router, tags=["rbac"])
