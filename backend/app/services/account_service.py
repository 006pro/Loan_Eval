from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.account_transaction import AccountTransaction
from app.models.client_profile import ClientProfile
from app.models.enums import AccountStatus, TransactionType
from app.models.virtual_account import VirtualAccount
from app.repositories import account_repository
from app.schemas.account import AccountTransactionOut, VirtualAccountOut

# Every client's Virtual Account is internal to this application (no external bank
# integration exists). Since there is no deposit/funding endpoint in the spec, a new
# account is opened with a fixed starter balance so the full loan lifecycle (approval
# fee payment, EMI, prepayment) can actually be exercised end-to-end.
REGISTRATION_STARTER_BALANCE = Decimal("500000.00")
_ACCOUNT_NOT_FOUND = "Virtual account not found"


def create_virtual_account(db: Session, client: ClientProfile) -> VirtualAccount:
    db.flush()
    account = VirtualAccount(
        client_id=client.id,
        account_number=f"VA{100000000 + client.id}",
        balance=Decimal("0.00"),
        status=AccountStatus.ACTIVE,
    )
    db.add(account)
    db.flush()
    _apply_delta(
        db,
        account=account,
        delta=REGISTRATION_STARTER_BALANCE,
        transaction_type=TransactionType.DEPOSIT,
        reference_type="REGISTRATION",
        reference_id=client.id,
    )
    return account


def get_account_out(db: Session, client_id: int) -> VirtualAccountOut:
    account = account_repository.get_by_client_id(db, client_id)
    if account is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, _ACCOUNT_NOT_FOUND)
    return VirtualAccountOut.model_validate(account)


def list_transactions_out(db: Session, client_id: int) -> list[AccountTransactionOut]:
    account = account_repository.get_by_client_id(db, client_id)
    if account is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, _ACCOUNT_NOT_FOUND)
    return [
        AccountTransactionOut.model_validate(txn) for txn in account_repository.list_transactions(db, account.id)
    ]


def get_locked_account_for_client(db: Session, client_id: int) -> VirtualAccount:
    account = db.execute(
        select(VirtualAccount).where(VirtualAccount.client_id == client_id).with_for_update()
    ).scalar_one_or_none()
    if account is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, _ACCOUNT_NOT_FOUND)
    return account


def credit(
    db: Session,
    account: VirtualAccount,
    amount: Decimal,
    transaction_type: TransactionType,
    reference_type: str,
    reference_id: int | None,
) -> AccountTransaction:
    return _apply_delta(db, account, amount, transaction_type, reference_type, reference_id)


def debit(
    db: Session,
    account: VirtualAccount,
    amount: Decimal,
    transaction_type: TransactionType,
    reference_type: str,
    reference_id: int | None,
) -> AccountTransaction:
    return _apply_delta(db, account, -amount, transaction_type, reference_type, reference_id)


def _apply_delta(
    db: Session,
    account: VirtualAccount,
    delta: Decimal,
    transaction_type: TransactionType,
    reference_type: str,
    reference_id: int | None,
) -> AccountTransaction:
    balance_before = Decimal(account.balance)
    balance_after = balance_before + delta
    if balance_after < 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Insufficient Virtual Account balance")

    account.balance = balance_after
    transaction = AccountTransaction(
        account_id=account.id,
        transaction_type=transaction_type,
        amount=abs(delta),
        balance_before=balance_before,
        balance_after=balance_after,
        reference_type=reference_type,
        reference_id=reference_id,
    )
    db.add(transaction)
    db.flush()
    return transaction
