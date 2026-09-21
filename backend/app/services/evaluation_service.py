from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.calculations.emi import calculate_emi
from app.calculations.fee import calculate_fee_amount
from app.models.enums import ApplicationStatus, AuditAction, EvaluationDecision, FeeStatus, LoanStatus
from app.models.loan import Loan
from app.models.loan_application import LoanApplication
from app.models.loan_evaluation import LoanEvaluation
from app.models.loan_fee import LoanFee
from app.repositories import admin_repository, loan_application_repository, loan_repository, master_repository
from app.schemas.evaluation import AdminClientSummary, AdminLoanApplicationOut, ApprovalRequest, RejectionRequest
from app.schemas.loan import LoanFeeOut, LoanOut
from app.services import audit_service


def _admin_profile_or_404(db: Session, user_id: int):
    admin = admin_repository.get_by_user_id(db, user_id)
    if admin is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Admin profile not found")
    return admin


def _application_or_404(db: Session, application_id: int) -> LoanApplication:
    application = loan_application_repository.get_by_id(db, application_id)
    if application is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Loan application not found")
    return application


def _to_admin_out(application: LoanApplication) -> AdminLoanApplicationOut:
    client = application.client
    return AdminLoanApplicationOut(
        id=application.id,
        client=AdminClientSummary(
            id=client.id,
            name=client.name,
            phone=client.phone,
            monthly_income=client.monthly_income,
            yearly_income=client.yearly_income,
            existing_loans=client.existing_loans,
            credit_score=client.credit_score,
        ),
        loan_type_id=application.loan_type_id,
        loan_type_name=application.loan_type.name,
        interest_rate=application.loan_type.interest_rate,
        requested_amount=application.requested_amount,
        requested_duration_months=application.requested_duration_months,
        requested_frequency=application.requested_frequency,
        status=application.status,
        rejection_reason=application.rejection_reason,
        submitted_at=application.submitted_at,
        evaluated_at=application.evaluated_at,
    )


def _to_loan_out(loan: Loan) -> LoanOut:
    fee_out = None
    if loan.fee is not None:
        fee_out = LoanFeeOut(
            id=loan.fee.id,
            fee_percentage=loan.fee.fee_percentage,
            fee_amount=loan.fee.fee_amount,
            status=loan.fee.status,
            calculated_at=loan.fee.calculated_at,
            paid_at=loan.fee.paid_at,
        )
    return LoanOut(
        id=loan.id,
        application_id=loan.application_id,
        loan_type_id=loan.loan_type_id,
        loan_type_name=loan.loan_type.name,
        approved_amount=loan.approved_amount,
        interest_rate=loan.interest_rate,
        duration_months=loan.duration_months,
        repayment_frequency=loan.repayment_frequency,
        emi_amount=loan.emi_amount,
        outstanding_principal=loan.outstanding_principal,
        start_date=loan.start_date,
        end_date=loan.end_date,
        status=loan.status,
        fee=fee_out,
    )


def list_applications(
    db: Session, *, status_filter: ApplicationStatus | None = None
) -> list[AdminLoanApplicationOut]:
    return [
        _to_admin_out(application)
        for application in loan_application_repository.list_all(db, application_status=status_filter)
    ]


def get_application(db: Session, application_id: int) -> AdminLoanApplicationOut:
    return _to_admin_out(_application_or_404(db, application_id))


def approve_application(
    db: Session, admin_user_id: int, application_id: int, payload: ApprovalRequest
) -> LoanOut:
    admin = _admin_profile_or_404(db, admin_user_id)
    application = _application_or_404(db, application_id)

    if application.status not in (ApplicationStatus.SUBMITTED, ApplicationStatus.UNDER_REVIEW):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Application already evaluated")

    loan_type = application.loan_type
    if not loan_type.is_active:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Selected loan type is not available")
    if not (loan_type.min_amount <= payload.approved_amount <= loan_type.max_amount):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid loan amount")

    fee_rule = master_repository.get_approval_fee_rule(db)
    if fee_rule is None:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Master configuration invalid")
    if not (fee_rule.minimum_fee_percent <= payload.approval_fee_percent <= fee_rule.maximum_fee_percent):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Approval fee exceeds configured maximum")

    interest_rate = Decimal(loan_type.interest_rate)
    approved_amount = Decimal(payload.approved_amount)
    emi_amount = calculate_emi(
        approved_amount, interest_rate, application.requested_duration_months, application.requested_frequency
    )
    fee_amount = calculate_fee_amount(approved_amount, Decimal(payload.approval_fee_percent))
    now = datetime.now(timezone.utc)

    db.add(
        LoanEvaluation(
            loan_application_id=application.id,
            admin_id=admin.id,
            credit_score=payload.credit_score,
            decision=EvaluationDecision.APPROVED,
            remarks=payload.remarks,
            evaluated_at=now,
        )
    )

    loan = Loan(
        application_id=application.id,
        client_id=application.client_id,
        loan_type_id=application.loan_type_id,
        approved_amount=approved_amount,
        interest_rate=interest_rate,
        duration_months=application.requested_duration_months,
        repayment_frequency=application.requested_frequency,
        emi_amount=emi_amount,
        outstanding_principal=approved_amount,
        status=LoanStatus.PENDING_FEE,
    )
    loan_repository.create_loan(db, loan)

    fee = LoanFee(
        loan_id=loan.id,
        fee_percentage=payload.approval_fee_percent,
        fee_amount=fee_amount,
        status=FeeStatus.PENDING,
        calculated_at=now,
    )
    loan_repository.create_fee(db, fee)

    application.status = ApplicationStatus.APPROVED
    application.evaluated_at = now

    audit_service.record(
        db,
        user_id=admin_user_id,
        action=AuditAction.LOAN_APPROVED,
        entity_type="LoanApplication",
        entity_id=application.id,
        new_value={"approved_amount": approved_amount, "approval_fee_percent": payload.approval_fee_percent},
    )
    audit_service.record(
        db,
        user_id=admin_user_id,
        action=AuditAction.APPROVAL_FEE_CREATED,
        entity_type="LoanFee",
        entity_id=fee.id,
        new_value={"fee_percentage": payload.approval_fee_percent, "fee_amount": fee_amount},
    )

    db.commit()
    db.refresh(loan)
    return _to_loan_out(loan_repository.get_by_id(db, loan.id))


def reject_application(
    db: Session, admin_user_id: int, application_id: int, payload: RejectionRequest
) -> AdminLoanApplicationOut:
    admin = _admin_profile_or_404(db, admin_user_id)
    application = _application_or_404(db, application_id)

    if application.status not in (ApplicationStatus.SUBMITTED, ApplicationStatus.UNDER_REVIEW):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Application already evaluated")

    now = datetime.now(timezone.utc)
    db.add(
        LoanEvaluation(
            loan_application_id=application.id,
            admin_id=admin.id,
            credit_score=payload.credit_score,
            decision=EvaluationDecision.REJECTED,
            remarks=payload.remarks,
            evaluated_at=now,
        )
    )

    application.status = ApplicationStatus.REJECTED
    application.rejection_reason = payload.rejection_reason
    application.evaluated_at = now

    audit_service.record(
        db,
        user_id=admin_user_id,
        action=AuditAction.LOAN_REJECTED,
        entity_type="LoanApplication",
        entity_id=application.id,
        new_value={"rejection_reason": payload.rejection_reason},
    )

    db.commit()
    db.refresh(application)
    return _to_admin_out(application)
