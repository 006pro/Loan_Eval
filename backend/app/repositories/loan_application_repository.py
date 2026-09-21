from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.enums import ApplicationStatus
from app.models.loan_application import LoanApplication


def create(db: Session, application: LoanApplication) -> LoanApplication:
    db.add(application)
    db.flush()
    return application


def get_by_id(db: Session, application_id: int) -> LoanApplication | None:
    return db.execute(
        select(LoanApplication)
        .options(joinedload(LoanApplication.loan_type), joinedload(LoanApplication.client))
        .where(LoanApplication.id == application_id)
    ).scalar_one_or_none()


def list_by_client(db: Session, client_id: int) -> list[LoanApplication]:
    return list(
        db.execute(
            select(LoanApplication)
            .options(joinedload(LoanApplication.loan_type))
            .where(LoanApplication.client_id == client_id)
            .order_by(LoanApplication.id.desc())
        ).scalars()
    )


def list_all(db: Session, *, application_status: ApplicationStatus | None = None) -> list[LoanApplication]:
    stmt = (
        select(LoanApplication)
        .options(joinedload(LoanApplication.loan_type), joinedload(LoanApplication.client))
        .order_by(LoanApplication.id.desc())
    )
    if application_status is not None:
        stmt = stmt.where(LoanApplication.status == application_status)
    return list(db.execute(stmt).scalars())
