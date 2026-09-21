from fastapi import APIRouter

from app.api.v1 import admin_master, auth, loan_types

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(loan_types.router)
api_router.include_router(admin_master.router)
