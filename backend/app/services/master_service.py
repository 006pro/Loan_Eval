from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.enums import AuditAction
from app.models.loan_type import LoanType
from app.models.penalty_rule import PenaltyRule
from app.repositories import master_repository
from app.schemas import master as schemas
from app.services import audit_service


def get_duration_rule(db: Session) -> schemas.DurationRuleOut:
    rule = master_repository.get_duration_rule(db)
    if rule is None:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Master configuration invalid")
    return schemas.DurationRuleOut.model_validate(rule)


def update_duration_rule(db: Session, admin_user_id: int, payload: schemas.DurationRuleUpdate) -> schemas.DurationRuleOut:
    rule = master_repository.get_duration_rule(db)
    if rule is None:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Master configuration invalid")

    old_value = {"minimum_months": rule.minimum_months, "maximum_months": rule.maximum_months}
    rule.minimum_months = payload.minimum_months
    rule.maximum_months = payload.maximum_months
    db.flush()

    audit_service.record(
        db,
        user_id=admin_user_id,
        action=AuditAction.MASTER_UPDATED,
        entity_type="DurationRule",
        entity_id=rule.id,
        old_value=old_value,
        new_value={"minimum_months": rule.minimum_months, "maximum_months": rule.maximum_months},
    )
    db.commit()
    return schemas.DurationRuleOut.model_validate(rule)


def get_approval_fee_rule(db: Session) -> schemas.ApprovalFeeRuleOut:
    rule = master_repository.get_approval_fee_rule(db)
    if rule is None:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Master configuration invalid")
    return schemas.ApprovalFeeRuleOut.model_validate(rule)


def update_approval_fee_rule(
    db: Session, admin_user_id: int, payload: schemas.ApprovalFeeRuleUpdate
) -> schemas.ApprovalFeeRuleOut:
    rule = master_repository.get_approval_fee_rule(db)
    if rule is None:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Master configuration invalid")

    old_value = {
        "minimum_fee_percent": rule.minimum_fee_percent,
        "maximum_fee_percent": rule.maximum_fee_percent,
    }
    rule.minimum_fee_percent = payload.minimum_fee_percent
    rule.maximum_fee_percent = payload.maximum_fee_percent
    db.flush()

    audit_service.record(
        db,
        user_id=admin_user_id,
        action=AuditAction.MASTER_UPDATED,
        entity_type="ApprovalFeeRule",
        entity_id=rule.id,
        old_value=old_value,
        new_value={
            "minimum_fee_percent": rule.minimum_fee_percent,
            "maximum_fee_percent": rule.maximum_fee_percent,
        },
    )
    db.commit()
    return schemas.ApprovalFeeRuleOut.model_validate(rule)


def list_loan_types(db: Session, *, active_only: bool = False) -> list[schemas.LoanTypeOut]:
    return [
        schemas.LoanTypeOut.model_validate(lt)
        for lt in master_repository.list_loan_types(db, active_only=active_only)
    ]


def get_loan_type_or_404(db: Session, loan_type_id: int) -> LoanType:
    loan_type = master_repository.get_loan_type(db, loan_type_id)
    if loan_type is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Loan type not found")
    return loan_type


def create_loan_type(db: Session, admin_user_id: int, payload: schemas.LoanTypeCreate) -> schemas.LoanTypeOut:
    loan_type = LoanType(**payload.model_dump())
    db.add(loan_type)
    db.flush()

    audit_service.record(
        db,
        user_id=admin_user_id,
        action=AuditAction.MASTER_UPDATED,
        entity_type="LoanType",
        entity_id=loan_type.id,
        old_value=None,
        new_value=payload.model_dump(),
    )
    db.commit()
    return schemas.LoanTypeOut.model_validate(loan_type)


def update_loan_type(
    db: Session, admin_user_id: int, loan_type_id: int, payload: schemas.LoanTypeUpdate
) -> schemas.LoanTypeOut:
    loan_type = get_loan_type_or_404(db, loan_type_id)
    old_value = {
        "name": loan_type.name,
        "interest_rate": loan_type.interest_rate,
        "min_amount": loan_type.min_amount,
        "max_amount": loan_type.max_amount,
        "is_active": loan_type.is_active,
    }

    changes = payload.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(loan_type, field, value)

    if loan_type.max_amount < loan_type.min_amount:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Master configuration invalid")

    db.flush()
    audit_service.record(
        db,
        user_id=admin_user_id,
        action=AuditAction.MASTER_UPDATED,
        entity_type="LoanType",
        entity_id=loan_type.id,
        old_value=old_value,
        new_value=changes,
    )
    db.commit()
    return schemas.LoanTypeOut.model_validate(loan_type)


def list_repayment_frequencies(db: Session, *, active_only: bool = False) -> list[schemas.RepaymentFrequencyOut]:
    return [
        schemas.RepaymentFrequencyOut.model_validate(freq)
        for freq in master_repository.list_repayment_frequencies(db, active_only=active_only)
    ]


def update_repayment_frequency(
    db: Session, admin_user_id: int, frequency_id: int, payload: schemas.RepaymentFrequencyUpdate
) -> schemas.RepaymentFrequencyOut:
    frequency = master_repository.get_repayment_frequency(db, frequency_id)
    if frequency is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Repayment frequency not found")

    old_value = {"is_active": frequency.is_active}
    frequency.is_active = payload.is_active
    db.flush()

    audit_service.record(
        db,
        user_id=admin_user_id,
        action=AuditAction.MASTER_UPDATED,
        entity_type="RepaymentFrequency",
        entity_id=frequency.id,
        old_value=old_value,
        new_value={"is_active": frequency.is_active},
    )
    db.commit()
    return schemas.RepaymentFrequencyOut.model_validate(frequency)


def _to_penalty_rule_out(rule: PenaltyRule) -> schemas.PenaltyRuleOut:
    return schemas.PenaltyRuleOut(
        id=rule.id,
        repayment_frequency=rule.repayment_frequency.code,
        calculation_frequency=rule.calculation_frequency,
        penalty_rate=rule.penalty_rate,
        is_active=rule.is_active,
    )


def list_penalty_rules(db: Session) -> list[schemas.PenaltyRuleOut]:
    return [_to_penalty_rule_out(rule) for rule in master_repository.list_penalty_rules(db)]


def update_penalty_rule(
    db: Session, admin_user_id: int, rule_id: int, payload: schemas.PenaltyRuleUpdate
) -> schemas.PenaltyRuleOut:
    rule = master_repository.get_penalty_rule(db, rule_id)
    if rule is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Penalty rule not found")

    old_value = {"penalty_rate": rule.penalty_rate, "is_active": rule.is_active}
    rule.penalty_rate = payload.penalty_rate
    if payload.is_active is not None:
        rule.is_active = payload.is_active
    db.flush()

    audit_service.record(
        db,
        user_id=admin_user_id,
        action=AuditAction.MASTER_UPDATED,
        entity_type="PenaltyRule",
        entity_id=rule.id,
        old_value=old_value,
        new_value={"penalty_rate": rule.penalty_rate, "is_active": rule.is_active},
    )
    db.commit()
    return _to_penalty_rule_out(rule)


def get_application_config(db: Session) -> schemas.ApplicationConfigOut:
    duration = master_repository.get_duration_rule(db)
    if duration is None:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Master configuration invalid")
    active_frequencies = master_repository.list_repayment_frequencies(db, active_only=True)
    return schemas.ApplicationConfigOut(
        minimum_duration_months=duration.minimum_months,
        maximum_duration_months=duration.maximum_months,
        active_repayment_frequencies=[freq.code for freq in active_frequencies],
    )
