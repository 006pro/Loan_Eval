from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import require_client
from app.models.user import User
from app.schemas.account import AccountTransactionOut, VirtualAccountOut
from app.services import account_service, client_service

router = APIRouter(prefix="/accounts", tags=["accounts"], dependencies=[Depends(require_client)])


@router.get("/me", response_model=VirtualAccountOut)
def get_my_account(db: Session = Depends(get_db), user: User = Depends(require_client)) -> VirtualAccountOut:
    client = client_service.get_profile_or_404(db, user)
    return account_service.get_account_out(db, client.id)


@router.get("/me/transactions", response_model=list[AccountTransactionOut])
def list_my_transactions(
    db: Session = Depends(get_db), user: User = Depends(require_client)
) -> list[AccountTransactionOut]:
    client = client_service.get_profile_or_404(db, user)
    return account_service.list_transactions_out(db, client.id)
