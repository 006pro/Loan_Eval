import enum


class UserRole(str, enum.Enum):
    CLIENT = "CLIENT"
    ADMIN = "ADMIN"


class ApplicationStatus(str, enum.Enum):
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class EvaluationDecision(str, enum.Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class LoanStatus(str, enum.Enum):
    PENDING_FEE = "PENDING_FEE"
    ACTIVE = "ACTIVE"
    OVERDUE = "OVERDUE"
    COMPLETED = "COMPLETED"


class FeeStatus(str, enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"


class ScheduleStatus(str, enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    OVERDUE = "OVERDUE"


class TransactionType(str, enum.Enum):
    DEPOSIT = "DEPOSIT"
    LOAN_DISBURSEMENT = "LOAN_DISBURSEMENT"
    APPROVAL_FEE_PAYMENT = "APPROVAL_FEE_PAYMENT"
    EMI_PAYMENT = "EMI_PAYMENT"
    PRINCIPAL_PREPAYMENT = "PRINCIPAL_PREPAYMENT"


class AccountStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"


class RepaymentFrequencyCode(str, enum.Enum):
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    HALF_YEARLY = "HALF_YEARLY"
    YEARLY = "YEARLY"


class CalculationFrequency(str, enum.Enum):
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"


class PaymentType(str, enum.Enum):
    EMI = "EMI"


class PenaltyStatus(str, enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"


class AuditAction(str, enum.Enum):
    LOGIN = "LOGIN"
    LOAN_APPLICATION_CREATED = "LOAN_APPLICATION_CREATED"
    MASTER_UPDATED = "MASTER_UPDATED"
    LOAN_APPROVED = "LOAN_APPROVED"
    LOAN_REJECTED = "LOAN_REJECTED"
    APPROVAL_FEE_CREATED = "APPROVAL_FEE_CREATED"
    APPROVAL_FEE_PAID = "APPROVAL_FEE_PAID"
    LOAN_ACTIVATED = "LOAN_ACTIVATED"
    LOAN_DISBURSED = "LOAN_DISBURSED"
    EMI_PAYMENT = "EMI_PAYMENT"
    PRINCIPAL_PREPAYMENT = "PRINCIPAL_PREPAYMENT"
    PENALTY_CREATED = "PENALTY_CREATED"
    LOAN_COMPLETED = "LOAN_COMPLETED"
    VIRTUAL_ACCOUNT_TRANSACTION = "VIRTUAL_ACCOUNT_TRANSACTION"
    ADMIN_CREATED = "ADMIN_CREATED"
