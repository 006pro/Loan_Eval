# API Reference

Base path: `/api/v1`. Interactive Swagger UI is served at `/docs` (OpenAPI JSON at
`/openapi.json`) when the backend is running.

Authentication: `Authorization: Bearer <token>`, issued by `/auth/login` or `/auth/register`.
Every endpoint below marked **CLIENT** or **ADMIN** requires that role's token; a client token on
an admin route (or vice versa) gets `403 Forbidden`, and a missing/invalid token gets
`401 Unauthorized`. A client can only ever see their own applications, loans, and account -
another client's resource ID returns `404 Not Found`, never `403` (so existence isn't leaked).

Money and rate fields are serialized as **strings** (e.g. `"12500.00"`) to preserve exact decimal
precision - parse them as decimals, not floats, on any client.

## Authentication

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/auth/register` | public | Create a CLIENT account, opens a funded Virtual Account, returns a token |
| POST | `/auth/login` | public | Returns a token for CLIENT or ADMIN |
| POST | `/auth/logout` | any | No-op (stateless JWT); `204` |
| GET | `/auth/me` | any | Current user's id, email, role, display name |

## Client Profile

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/clients/me` | CLIENT | Own profile |
| PUT | `/clients/me` | CLIENT | Update own profile (partial update) |

## Loan Types (public catalogue)

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/loan-types` | public | Active loan types only |
| GET | `/loan-types/{id}` | public | One loan type |

## Loan Applications

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/loan-applications/config` | CLIENT | Current duration range + active repayment frequencies, for the application form |
| POST | `/loan-applications/preview` | CLIENT | Backend-calculated EMI/interest/total payable for a hypothetical application (no DB write) |
| POST | `/loan-applications` | CLIENT | Submit an application; validated against current Master config and a completed profile |
| GET | `/loan-applications` | CLIENT | List own applications |
| GET | `/loan-applications/{id}` | CLIENT | One own application, including `rejection_reason` if rejected |

## Admin - Loan Evaluation

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/admin/loan-applications?status=` | ADMIN | List applications, optional status filter |
| GET | `/admin/loan-applications/{id}` | ADMIN | Application detail with client summary |
| POST | `/admin/loan-applications/{id}/approve` | ADMIN | `{approved_amount, approval_fee_percent, credit_score?, remarks?}` -> creates `Loan` (`PENDING_FEE`) + `LoanFee` |
| POST | `/admin/loan-applications/{id}/reject` | ADMIN | `{rejection_reason, credit_score?, remarks?}` - reason is mandatory |

## Admin - Loans

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/admin/loans?status=` | ADMIN | List all loans, optional status filter |
| GET | `/admin/loans/{id}` | ADMIN | Loan detail |
| GET | `/admin/loans/{id}/schedule` | ADMIN | Full repayment schedule |

## Admin - Master Configuration

| Method | Path | Auth | Description |
|---|---|---|---|
| GET / PUT | `/admin/master/duration` | ADMIN | `{minimum_months, maximum_months}` |
| GET / PUT | `/admin/master/fees` | ADMIN | `{minimum_fee_percent, maximum_fee_percent}` |
| GET | `/admin/master/loan-types` | ADMIN | All loan types, including inactive |
| POST | `/admin/master/loan-types` | ADMIN | Create a loan type |
| PUT | `/admin/master/loan-types/{id}` | ADMIN | Partial update (name, rate, amounts, `is_active`) |
| GET | `/admin/master/repayment-frequencies` | ADMIN | All four frequencies with `is_active` |
| PUT | `/admin/master/repayment-frequencies/{id}` | ADMIN | `{is_active}` |
| GET | `/admin/master/penalties` | ADMIN | All penalty rules |
| PUT | `/admin/master/penalties/{id}` | ADMIN | `{penalty_rate, is_active?}` |

Every Master write is recorded to `/admin/audit-logs` with the old and new value.

## Admin - Audit Logs

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/admin/audit-logs?limit=` | ADMIN | Most recent entries first (default 200, max 1000) |

## Loans (client)

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/loans` | CLIENT | Own loans |
| GET | `/loans/{id}` | CLIENT | Own loan detail (lazily assesses overdue/penalty first) |
| GET | `/loans/{id}/schedule` | CLIENT | Full repayment schedule |
| GET | `/loans/{id}/fee` | CLIENT | Approval fee detail |
| POST | `/loans/{id}/fee/pay` | CLIENT | Pay the approval fee - debits Virtual Account, disburses funds, generates schedule, activates loan (one transaction) |
| POST | `/loans/{id}/payment` | CLIENT | Pay the next due installment in full (partial payment is not possible - there is no amount field) |
| GET | `/loans/{id}/payments` | CLIENT | Payment history |
| POST | `/loans/{id}/prepayment` | CLIENT | `{amount}` - reduces outstanding principal immediately; re-amortizes only the still-unpaid installments |

## Virtual Account

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/accounts/me` | CLIENT | Account number, balance, status |
| GET | `/accounts/me/transactions` | CLIENT | Full ledger, most recent first |

## Error Format

```json
{ "detail": "Insufficient Virtual Account balance" }
```

`detail` is a plain string for business-rule violations (`400`), auth failures (`401`/`403`), and
not-found (`404`). Pydantic validation errors (`422`) return `detail` as a list of
`{loc, msg, type}` objects, matching FastAPI's default shape. Unhandled server errors return a
generic `500` with `{"detail": "Internal server error"}` - no stack trace is ever exposed.
