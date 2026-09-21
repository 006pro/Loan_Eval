from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.approval_fee_rule import ApprovalFeeRule
from app.models.duration_rule import DurationRule
from app.models.enums import RepaymentFrequencyCode
from app.models.loan_type import LoanType
from app.models.penalty_rule import PenaltyRule
from app.models.repayment_frequency import RepaymentFrequency


def get_duration_rule(db: Session) -> DurationRule | None:
    return db.execute(select(DurationRule).order_by(DurationRule.id).limit(1)).scalar_one_or_none()


def get_approval_fee_rule(db: Session) -> ApprovalFeeRule | None:
    return db.execute(select(ApprovalFeeRule).order_by(ApprovalFeeRule.id).limit(1)).scalar_one_or_none()


def list_loan_types(db: Session, *, active_only: bool = False) -> list[LoanType]:
    stmt = select(LoanType).order_by(LoanType.id)
    if active_only:
        stmt = stmt.where(LoanType.is_active.is_(True))
    return list(db.execute(stmt).scalars())


def get_loan_type(db: Session, loan_type_id: int) -> LoanType | None:
    return db.get(LoanType, loan_type_id)


def list_repayment_frequencies(db: Session, *, active_only: bool = False) -> list[RepaymentFrequency]:
    stmt = select(RepaymentFrequency).order_by(RepaymentFrequency.id)
    if active_only:
        stmt = stmt.where(RepaymentFrequency.is_active.is_(True))
    return list(db.execute(stmt).scalars())


def get_repayment_frequency(db: Session, frequency_id: int) -> RepaymentFrequency | None:
    return db.get(RepaymentFrequency, frequency_id)


def get_repayment_frequency_by_code(db: Session, code: RepaymentFrequencyCode) -> RepaymentFrequency | None:
    return db.execute(
        select(RepaymentFrequency).where(RepaymentFrequency.code == code)
    ).scalar_one_or_none()


def list_penalty_rules(db: Session) -> list[PenaltyRule]:
    return list(db.execute(select(PenaltyRule).order_by(PenaltyRule.id)).scalars())


def get_penalty_rule(db: Session, rule_id: int) -> PenaltyRule | None:
    return db.get(PenaltyRule, rule_id)


def get_penalty_rule_by_frequency_code(db: Session, code: RepaymentFrequencyCode) -> PenaltyRule | None:
    return db.execute(
        select(PenaltyRule).join(RepaymentFrequency).where(RepaymentFrequency.code == code)
    ).scalar_one_or_none()
