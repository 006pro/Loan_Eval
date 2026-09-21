# Database

MySQL 8, managed with Alembic migrations (`backend/alembic/versions/`). All money fields are
`DECIMAL(14,2)`; percentage/rate fields are `DECIMAL(5,2)`. Every table has `created_at` (and
`updated_at` where the row is ever edited in place).

## Entities

### Identity

| Table | Key columns | Notes |
|---|---|---|
| `users` | `email` (unique), `password_hash`, `role` | `role`: `CLIENT` \| `ADMIN` |
| `client_profiles` | `user_id` (unique FK), `name`, `phone`, `address`, `date_of_birth`, `employment`, `monthly_income`, `yearly_income`, `existing_loans`, `bank_account_number`, `credit_score` | 1:1 with `users` |
| `admin_profiles` | `user_id` (unique FK), `employee_id` (unique), `name` | 1:1 with `users` |

### Master / Configuration

| Table | Key columns | Notes |
|---|---|---|
| `loan_types` | `name` (unique), `interest_rate`, `min_amount`, `max_amount`, `is_active` | |
| `duration_rules` | `minimum_months`, `maximum_months` | singleton row |
| `approval_fee_rules` | `minimum_fee_percent`, `maximum_fee_percent` | singleton row |
| `repayment_frequencies` | `code` (unique: MONTHLY/QUARTERLY/HALF_YEARLY/YEARLY), `is_active` | |
| `penalty_rules` | `repayment_frequency_id` (unique FK), `calculation_frequency` (DAILY/WEEKLY), `penalty_rate`, `is_active` | one row per frequency |

### Loan Lifecycle

| Table | Key columns | Notes |
|---|---|---|
| `loan_applications` | `client_id` FK, `loan_type_id` FK, `requested_amount`, `requested_duration_months`, `requested_frequency`, `status`, `rejection_reason`, `submitted_at`, `evaluated_at` | |
| `loan_evaluations` | `loan_application_id` (unique FK), `admin_id` FK, `credit_score`, `decision`, `remarks`, `evaluated_at` | one per application |
| `loans` | `application_id` (unique FK), `client_id` FK, `loan_type_id` FK, `approved_amount`, `interest_rate`, `duration_months`, `repayment_frequency`, `emi_amount`, `outstanding_principal`, `start_date`, `end_date`, `status` | `interest_rate`/`duration_months`/`repayment_frequency` are **frozen** at approval time |
| `loan_fees` | `loan_id` (unique FK), `fee_percentage`, `fee_amount`, `status`, `calculated_at`, `paid_at` | |
| `repayment_schedules` | `loan_id` FK, `installment_number`, `due_date`, `opening_principal`, `scheduled_principal`, `scheduled_interest`, `scheduled_amount`, `paid_principal`, `paid_interest`, `paid_amount`, `remaining_principal`, `status`, `paid_at` | unique `(loan_id, installment_number)` |
| `payments` | `loan_id` FK, `schedule_id` FK, `account_transaction_id` FK, `payment_type`, `amount`, `principal_amount`, `interest_amount`, `penalty_amount`, `payment_date` | one row per EMI payment |
| `prepayments` | `loan_id` FK, `client_id` FK, `account_transaction_id` FK, `amount`, `principal_reduction` | |
| `penalties` | `loan_id` FK, `schedule_id` FK, `overdue_amount`, `overdue_days`, `penalty_rate`, `calculation_frequency`, `penalty_amount`, `status` | |

### Financial Ledger

| Table | Key columns | Notes |
|---|---|---|
| `virtual_accounts` | `client_id` (unique FK), `account_number` (unique), `balance`, `status` | 1:1 with `client_profiles` |
| `account_transactions` | `account_id` FK, `transaction_type`, `amount`, `balance_before`, `balance_after`, `reference_type`, `reference_id` | append-only ledger; balance is never mutated without a matching row here |

### Audit

| Table | Key columns | Notes |
|---|---|---|
| `audit_logs` | `user_id` FK (nullable), `action`, `entity_type`, `entity_id`, `old_value`, `new_value` (JSON text) | written for logins, applications, master changes, approvals/rejections, fee/disbursement events, EMI payments, prepayments, penalty creation, and loan completion |

## Relationships

```text
User 1---1 ClientProfile 1---1 VirtualAccount 1---N AccountTransaction
User 1---1 AdminProfile

ClientProfile 1---N LoanApplication N---1 LoanType
LoanApplication 1---1 LoanEvaluation N---1 AdminProfile
LoanApplication 1---1 Loan N---1 LoanType

Loan 1---1 LoanFee
Loan 1---N RepaymentSchedule 1---1 Penalty (0 or 1 per installment)
Loan 1---N Payment N---1 RepaymentSchedule
Loan 1---N Prepayment

Payment N---1 AccountTransaction
Prepayment N---1 AccountTransaction

RepaymentFrequency 1---1 PenaltyRule
```

## Constraints and Integrity

- Foreign keys on every relationship above; `ON DELETE` is left at MySQL's default (`RESTRICT`)
  since financial history must never be silently deleted.
- Unique constraints: `users.email`, `admin_profiles.employee_id`, `virtual_accounts.client_id`
  and `.account_number`, `loans.application_id`, `loan_fees.loan_id`,
  `(repayment_schedules.loan_id, installment_number)`, `penalty_rules.repayment_frequency_id`.
- `NOT NULL` on every column that has no legitimate "unset" state (amounts, rates, statuses,
  foreign keys); profile fields collected progressively after registration (`phone`, `address`,
  income, etc.) are nullable until the client completes their profile.
- All monetary columns are `DECIMAL(14,2)`; all percentage/rate columns are `DECIMAL(5,2)`.
  `FLOAT`/`DOUBLE` are never used for money.
- Concurrency safety uses `SELECT ... FOR UPDATE` row locks (on `VirtualAccount` and on the next
  payable `RepaymentSchedule` row) inside each financial service function's single transaction,
  rather than relying on frontend validation or optimistic retries.

## Historical Accuracy

`loans.interest_rate`, `loans.duration_months`, `loans.repayment_frequency`, and
`loan_fees.fee_percentage`/`fee_amount` are copied from Master configuration **at the moment of
approval** and stored directly on the row. Master tables (`loan_types`, `duration_rules`,
`approval_fee_rules`, `penalty_rules`) are read only when creating new records; no query ever
joins a historical `Loan`/`RepaymentSchedule` back to the live Master tables for its figures, so
an admin changing Master configuration later cannot alter any existing loan's numbers.
