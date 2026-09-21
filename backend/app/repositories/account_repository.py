from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.account_transaction import AccountTransaction
from app.models.virtual_account import VirtualAccount


def get_by_client_id(db: Session, client_id: int) -> VirtualAccount | None:
    return db.execute(select(VirtualAccount).where(VirtualAccount.client_id == client_id)).scalar_one_or_none()


def list_transactions(db: Session, account_id: int) -> list[AccountTransaction]:
    return list(
        db.execute(
            select(AccountTransaction)
            .where(AccountTransaction.account_id == account_id)
            .order_by(AccountTransaction.id.desc())
        ).scalars()
    )
