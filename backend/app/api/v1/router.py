from fastapi import APIRouter

from app.api.v1 import (
    accounts,
    admin_audit_logs,
    admin_loan_applications,
    admin_master,
    auth,
    clients,
    loan_applications,
    loan_types,
    loans,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(clients.router)
api_router.include_router(loan_types.router)
api_router.include_router(loan_applications.router)
api_router.include_router(admin_loan_applications.router)
api_router.include_router(admin_master.router)
api_router.include_router(admin_audit_logs.router)
api_router.include_router(loans.router)
api_router.include_router(accounts.router)
