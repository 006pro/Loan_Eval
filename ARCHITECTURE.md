# Architecture

## System Architecture

A modular monolith. One FastAPI process serves the whole API; one MySQL database holds all
state. The React frontend never talks to the database directly and performs no financial
calculations of its own - the backend is the single source of truth for every number the user
sees.

```text
React Frontend (Vite, TypeScript)
            |  fetch(), JWT bearer token
            v
FastAPI Routers            app/api/v1/*.py   - request/response only
            |
Service Layer              app/services/*.py - validation, orchestration, transactions
            |
Calculation Layer          app/calculations/*.py - EMI, schedule, fee, penalty math
            |
Repository Layer           app/repositories/*.py - SQLAlchemy queries
            |
SQLAlchemy ORM / MySQL
```

Routers depend only on services (never repositories or models directly, beyond passing IDs).
Services depend on repositories and calculations. Repositories are the only layer that builds
SQLAlchemy `select()`/`insert()` statements. This keeps business rules out of both the routers
and the raw query code.

## Modules

- **auth** - registration, login, JWT issuance/verification, Argon2 hashing, role dependencies
  (`require_client`, `require_admin`).
- **master** - the five configurable rule sets: `LoanType`, `DurationRule`, `ApprovalFeeRule`,
  `RepaymentFrequency`, `PenaltyRule`. Admin-only write access, audit-logged.
- **loan applications** - client submission, backend-calculated preview, Master-driven
  validation (loan type active + amount range, current duration range, active frequency).
- **evaluation** - admin approve/reject. Approval freezes interest rate/duration/frequency onto
  a new `Loan` (status `PENDING_FEE`) and creates its `LoanFee`; rejection requires a reason.
- **financial system** - `VirtualAccount`/`AccountTransaction` ledger, approval fee payment
  (which also disburses funds and generates the repayment schedule), EMI payment, principal
  prepayment, and lazy overdue/penalty assessment.
- **audit** - `AuditLog` entries for logins, application submission, master changes, approvals,
  rejections, fee events, disbursement, EMI payments, prepayments, penalties, and completion.

## Data Flow: Approving a Loan and Activating It

```text
ADMIN POST /admin/loan-applications/{id}/approve
    -> evaluation_service.approve_application
       - validate application is still evaluable
       - validate approved_amount against LoanType range
       - validate fee % against current ApprovalFeeRule
       - freeze interest_rate/duration/frequency onto a new Loan (PENDING_FEE)
       - create LoanFee (PENDING)
       - AuditLog: LOAN_APPROVED, APPROVAL_FEE_CREATED
       - COMMIT

CLIENT POST /loans/{id}/fee/pay
    -> fee_service.pay_approval_fee   (single DB transaction)
       - lock the Virtual Account row (SELECT ... FOR UPDATE)
       - debit fee amount -> AccountTransaction(APPROVAL_FEE_PAYMENT)
       - mark LoanFee PAID
       - credit approved amount -> AccountTransaction(LOAN_DISBURSEMENT)
       - generate RepaymentSchedule rows (reducing-balance amortization)
       - set Loan.status = ACTIVE, start_date/end_date
       - AuditLog: APPROVAL_FEE_PAID, LOAN_DISBURSED, LOAN_ACTIVATED
       - COMMIT (or ROLLBACK everything on any failure, e.g. insufficient balance)
```

## Loan Lifecycle

```text
LoanApplication: SUBMITTED -> (UNDER_REVIEW) -> APPROVED | REJECTED
Loan:            PENDING_FEE -> ACTIVE -> [OVERDUE <-> ACTIVE] -> COMPLETED
LoanFee:         PENDING -> PAID
RepaymentSchedule (per installment): PENDING -> [OVERDUE] -> PAID
```

`Loan.status` is derived, never assumed:
- `OVERDUE` is set when an installment's due date has passed unpaid (checked lazily on read/pay
  - see below).
- `ACTIVE` is restored once no installment remains overdue.
- `COMPLETED` requires `outstanding_principal <= 0` **and** no remaining `PENDING`/`OVERDUE`
  installments (`app/services/loan_service.py::refresh_loan_status_after_payment`).

## Master Configuration

Master tables are singleton or small reference rows, edited in place:

```text
DurationRule          (minimum_months, maximum_months)               - 1 row
ApprovalFeeRule       (minimum_fee_percent, maximum_fee_percent)     - 1 row
LoanType              (name, interest_rate, min/max amount, active)  - many rows
RepaymentFrequency    (code, is_active)                              - 4 rows
PenaltyRule           (repayment_frequency, calculation_frequency,
                        penalty_rate, is_active)                     - 4 rows
```

Every update goes through `app/services/master_service.py`, which validates the new value,
persists it, and writes an `AuditLog` row with the old and new values. Master rows are read only
when *creating* a new `LoanApplication` or `Loan` - they are never joined back into historical
reads, so a later Master change cannot retroactively change what an existing loan shows.

## Financial Transactions

Every balance-changing operation is wrapped in one database transaction and always produces an
`AccountTransaction` row (`app/services/account_service.py::_apply_delta`) - the Virtual Account
balance is never mutated directly. Concurrent double-spend is prevented with
`SELECT ... FOR UPDATE` row locks on the account and on the next payable installment
(`app/repositories/account_repository.py`'s locked variants, `schedule_repository.get_next_payable`).

Because there is no background scheduler in this project's scope, overdue detection and penalty
accrual run **lazily**: whenever a client or admin reads a loan/schedule, or the client attempts
a payment, `app/services/penalty_service.py::assess_loan` checks each pending installment's due
date, marks it `OVERDUE` if needed, and accrues/updates its `Penalty` row using the Master
`PenaltyRule` for that loan's repayment frequency.

## Security

- Passwords hashed with Argon2 (`argon2-cffi`), never stored or logged in plain text.
- JWT bearer tokens (HS256, secret from `.env`) with a subject (`user.id`) and `role` claim.
- `require_client` / `require_admin` FastAPI dependencies enforce role separation on every
  protected route; ownership checks (`client_id` match) prevent one client from reading another
  client's applications, loans, or transactions (enforced in the service layer, not just the UI).
- A catch-all exception handler (`app/main.py`) returns a generic `500` body and logs the real
  exception server-side, so internal errors and stack traces are never exposed to clients.
