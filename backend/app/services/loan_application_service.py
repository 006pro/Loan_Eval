from datetime import date
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.calculations.repayment import generate_schedule, summarize
from app.models.client_profile import ClientProfile
from app.models.enums import ApplicationStatus, AuditAction
from app.models.loan_application import LoanApplication
from app.models.loan_type import LoanType
from app.repositories import loan_application_repository, master_repository
from app.schemas.loan_application import LoanApplicationOut, LoanApplicationPreviewOut, LoanApplicationRequest
from app.services import audit_service, client_service


def _validate_and_resolve_loan_type(db: Session, payload: LoanApplicationRequest) -> LoanType:
    loan_type = master_repository.get_loan_type(db, payload.loan_type_id)
    if loan_type is None or not loan_type.is_active:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Selected loan type is not available")

    if payload.requested_amount < loan_type.min_amount or payload.requested_amount > loan_type.max_amount:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid loan amount")

    duration_rule = master_repository.get_duration_rule(db)
    if duration_rule is None:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Master configuration invalid")
    if not (duration_rule.minimum_months <= payload.requested_duration_months <= duration_rule.maximum_months):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid loan duration")

    frequency = master_repository.get_repayment_frequency_by_code(db, payload.requested_frequency)
    if frequency is None or not frequency.is_active:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid repayment frequency")

    return loan_type


def preview_application(db: Session, payload: LoanApplicationRequest) -> LoanApplicationPreviewOut:
    loan_type = _validate_and_resolve_loan_type(db, payload)
    rows = generate_schedule(
        Decimal(payload.requested_amount),
        Decimal(loan_type.interest_rate),
        payload.requested_duration_months,
        payload.requested_frequency,
        date.today(),
    )
    total_interest, total_payable = summarize(rows)
    installment_amount = rows[0].installment_amount if rows else Decimal("0.00")

    return LoanApplicationPreviewOut(
        loan_type_id=loan_type.id,
        loan_type_name=loan_type.name,
        requested_amount=payload.requested_amount,
        interest_rate=loan_type.interest_rate,
        duration_months=payload.requested_duration_months,
        repayment_frequency=payload.requested_frequency,
        number_of_installments=len(rows),
        estimated_installment_amount=installment_amount,
        estimated_total_interest=total_interest,
        estimated_total_payable=total_payable,
    )


def _to_out(application: LoanApplication) -> LoanApplicationOut:
    return LoanApplicationOut(
        id=application.id,
        loan_type_id=application.loan_type_id,
        loan_type_name=application.loan_type.name,
        requested_amount=application.requested_amount,
        requested_duration_months=application.requested_duration_months,
        requested_frequency=application.requested_frequency,
        status=application.status,
        rejection_reason=application.rejection_reason,
        submitted_at=application.submitted_at,
        evaluated_at=application.evaluated_at,
    )


def submit_application(
    db: Session, client: ClientProfile, user_id: int, payload: LoanApplicationRequest
) -> LoanApplicationOut:
    if not client_service.is_profile_complete(client):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Complete your profile before applying for a loan")

    _validate_and_resolve_loan_type(db, payload)

    application = LoanApplication(
        client_id=client.id,
        loan_type_id=payload.loan_type_id,
        requested_amount=payload.requested_amount,
        requested_duration_months=payload.requested_duration_months,
        requested_frequency=payload.requested_frequency,
        status=ApplicationStatus.SUBMITTED,
    )
    loan_application_repository.create(db, application)

    audit_service.record(
        db,
        user_id=user_id,
        action=AuditAction.LOAN_APPLICATION_CREATED,
        entity_type="LoanApplication",
        entity_id=application.id,
        new_value={
            "loan_type_id": payload.loan_type_id,
            "requested_amount": payload.requested_amount,
            "requested_duration_months": payload.requested_duration_months,
            "requested_frequency": payload.requested_frequency,
        },
    )
    db.commit()
    db.refresh(application)
    return _to_out(application)


def get_application_for_client(db: Session, client: ClientProfile, application_id: int) -> LoanApplicationOut:
    application = loan_application_repository.get_by_id(db, application_id)
    if application is None or application.client_id != client.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Loan application not found")
    return _to_out(application)


def list_applications_for_client(db: Session, client: ClientProfile) -> list[LoanApplicationOut]:
    return [_to_out(application) for application in loan_application_repository.list_by_client(db, client.id)]
