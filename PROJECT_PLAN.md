# Project Plan — Loan Management and Evaluation System

## 1. Architecture

```
React (TypeScript, Vite) Frontend
            |
       FastAPI REST API  (/api/v1)
            |
       Router Layer            (app/api)
            |
       Service Layer           (app/services)
            |
       Business/Calculation    (app/calculations)
            |
       Repository/SQLAlchemy   (app/repositories, app/models)
            |
          MySQL
```

Modular monolith. Business logic lives in services, never in routers.
Money is always `Decimal` / SQL `DECIMAL`, never float.

## 2. Database Entities

- `User` (email, hashed_password, role: CLIENT|ADMIN)
- `ClientProfile` (1:1 User)
- `AdminProfile` (1:1 User)
- `VirtualAccount` (1:1 ClientProfile)
- `AccountTransaction` (N:1 VirtualAccount)
- `LoanType` (master)
- `DurationRule` (master, singleton row)
- `ApprovalFeeRule` (master, singleton row)
- `RepaymentFrequency` (master, reference table: MONTHLY/QUARTERLY/HALF_YEARLY/YEARLY, is_active)
- `PenaltyRule` (master, one row per RepaymentFrequency)
- `LoanApplication` (N:1 ClientProfile, N:1 LoanType)
- `LoanEvaluation` (1:1 LoanApplication, N:1 AdminProfile)
- `Loan` (1:1 LoanApplication, N:1 ClientProfile, N:1 LoanType) — stores interest_rate, duration_months, repayment_frequency **as actually used**, immune to later master edits
- `LoanFee` (1:1 Loan)
- `RepaymentSchedule` (N:1 Loan)
- `Payment` (N:1 Loan, N:1 RepaymentSchedule, N:1 AccountTransaction)
- `Prepayment` (N:1 Loan, N:1 ClientProfile, N:1 AccountTransaction)
- `Penalty` (N:1 Loan, N:1 RepaymentSchedule)
- `AuditLog` (N:1 User)

Historical accuracy rule: `Loan`, `LoanFee`, `RepaymentSchedule`, `Penalty` freeze the numeric
values effective at the time they were created. Master tables are only read when *creating* new
records, never joined into historical reads for financial figures.

## 3. Master Configuration Design

Master tables are singleton/reference rows edited in place by ADMIN via `/api/v1/admin/master/*`.
Every update:
1. validates the new value(s),
2. writes to MySQL,
3. writes an `AuditLog` row with old/new value,
4. is picked up by the *next* application/approval/payment — never mutates existing `Loan`/
   `LoanApplication`/`RepaymentSchedule` rows.

## 4. Business Rules Summary

- Loan application validated against: LoanType active + amount range, DurationRule min/max,
  RepaymentFrequency active.
- Approval fee % validated against ApprovalFeeRule min/max at approval time; fee amount is
  server-calculated, never admin-entered.
- Approval never activates a loan directly — it creates `Loan` in `PENDING_FEE` + `LoanFee` in
  `PENDING`.
- Fee payment is one atomic transaction: debit virtual account → mark fee PAID → credit loan
  amount → activate loan → generate schedule → audit log. Any failure rolls back everything.
- EMI payments must match the scheduled amount exactly (no partial payments).
- Prepayments reduce outstanding principal immediately; recalculated EMI/interest apply from the
  next unpaid installment only, historical schedule rows are untouched.
- Overdue installments accrue penalties using the `PenaltyRule` for the loan's repayment
  frequency (daily for MONTHLY, weekly otherwise).
- Loan completion is derived from outstanding principal reaching zero, not from an EMI call
  succeeding.
- Row-level locking (`SELECT ... FOR UPDATE` via SQLAlchemy `with_for_update`) plus unique
  constraints protect virtual account balance and fee/approval operations from concurrent
  double-submission.

## 5. API Structure

`/api/v1/auth`, `/api/v1/clients`, `/api/v1/loan-types`, `/api/v1/loan-applications`,
`/api/v1/admin/loan-applications`, `/api/v1/admin/master/*`, `/api/v1/loans`,
`/api/v1/loans/{id}/fee`, `/api/v1/loans/{id}/payment`, `/api/v1/loans/{id}/prepayment`,
`/api/v1/accounts/me` — matching PROMPT.MD section 41.

## 6. Frontend Pages

Client: Login, Register, Dashboard, Profile, Loan Types, Apply for Loan, My Applications,
Application Details, My Loans, Loan Details, Repayment Schedule, Approval Fee, Virtual Account,
Transaction History.

Admin: Login, Dashboard, Loan Applications, Application Details, Loans, Loan Details, Master
Configuration (Loan Types / Duration / Fee / Frequencies / Penalties), Audit Logs.

Navy/blue professional theme, plain CSS, no UI kit.

## 7. Implementation Phases (commit after each)

1. Foundation — backend/frontend scaffolding, env config, MySQL connectivity check
2. Database — SQLAlchemy models, relationships, Alembic migrations
3. Authentication — register/login, JWT, Argon2, role guards
4. Master management — models + services + API + admin UI
5. Loan application — client profile, application CRUD, preview calculation, EMI module
6. Admin evaluation — review, approve/reject, fee calculation
7. Financial system — virtual account, fee payment transaction, disbursement, schedule
   generation, EMI payment, prepayment, penalties, completion
8. Frontend integration — wire every page to real endpoints
9. Testing — pytest suite per PROMPT.MD section 59
10. Final review — cleanup, docs (README/ARCHITECTURE/DATABASE/API), security pass, push

## 8. Out of Scope (per spec)

Docker, cloud providers, Kubernetes, CI/CD, Redis, Kafka, Celery, microservices, Nginx config.
