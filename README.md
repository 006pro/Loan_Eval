# Loan Management and Evaluation System

A local full-stack loan management, evaluation, and repayment platform. Two roles - **CLIENT**
and **ADMIN** - covering client onboarding, loan applications, admin evaluation, approval fees,
an internal Virtual Bank Account, EMI repayment, prepayments, and overdue penalties.

See also: [ARCHITECTURE.md](ARCHITECTURE.md), [DATABASE.md](DATABASE.md), [API.md](API.md).

## Technology Stack

- **Backend**: Python 3.12, FastAPI, SQLAlchemy 2.x, Alembic, Pydantic v2, JWT (PyJWT), Argon2
  password hashing, Pytest
- **Frontend**: React 18, TypeScript, Vite, plain CSS
- **Database**: MySQL 8

No Docker, cloud services, or job queues are used - everything runs directly on your machine.

## Prerequisites

- Python 3.12 (SQLAlchemy/Pydantic/argon2-cffi wheels are most reliably available for 3.12;
  very new Python versions may require compiling some dependencies from source)
- Node.js 18+ and npm
- MySQL Server 8.0+, running locally

## MySQL Setup

1. Start your local MySQL server.
2. Create the database and an application user (adjust the password):

   ```sql
   CREATE DATABASE loan_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'loan_app'@'localhost' IDENTIFIED BY 'choose-a-password';
   GRANT ALL PRIVILEGES ON loan_management.* TO 'loan_app'@'localhost';
   FLUSH PRIVILEGES;
   ```

## Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Edit `backend/.env`:

```env
DATABASE_URL=mysql+pymysql://loan_app:choose-a-password@localhost:3306/loan_management
JWT_SECRET_KEY=replace-with-a-long-random-local-secret
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Run the database migrations:

```bash
alembic upgrade head
```

Load initial Master configuration, sample loan types, an admin account, and a demo client
(safe to re-run; every insert is guarded by an existence check):

```bash
python seed.py
```

This prints the seeded credentials, by default:

- Admin: `admin@loanms.com` / `Admin@12345`
- Demo client: `client@loanms.com` / `Client@12345` (starts with a demo Virtual Account balance)

Start the API:

```bash
uvicorn app.main:app --reload
```

The API is now available at `http://localhost:8000`, with interactive Swagger documentation at
`http://localhost:8000/docs`.

## Frontend Setup

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

The frontend runs at `http://localhost:5173` and expects the backend at
`http://localhost:8000/api/v1` (configurable via `frontend/.env`'s `VITE_API_BASE_URL`).

## Running Tests

```bash
cd backend
venv\Scripts\activate
pytest
```

Tests run against a separate `loan_management_test` MySQL database (create it once with
`CREATE DATABASE loan_management_test;` granted to the same user) so they never touch your
development data. Tables are created/dropped automatically; each test runs inside a rolled-back
transaction.

To verify the frontend compiles and builds cleanly:

```bash
cd frontend
npm run build
```

## Everyday Use

1. Start MySQL.
2. `cd backend && venv\Scripts\activate && uvicorn app.main:app --reload`
3. `cd frontend && npm run dev`
4. Open `http://localhost:5173`, log in as the seeded admin or client, or register a new client.

## Project Structure

```text
backend/
  app/
    api/v1/        FastAPI routers (thin - no business logic)
    core/          settings, security (JWT, Argon2)
    db/            SQLAlchemy engine/session, declarative base
    models/        ORM entities and enums
    schemas/       Pydantic request/response models
    repositories/  query functions, one module per aggregate
    services/      business logic and orchestration
    calculations/  EMI, repayment schedule, fee, and penalty math
  alembic/         migrations
  tests/           pytest suite
  seed.py          development seed script

frontend/
  src/
    pages/client/  client-facing pages
    pages/admin/   admin-facing pages (including Master Configuration tabs)
    layouts/       sidebar shells for each role
    services/      typed fetch wrappers per API area
    hooks/         auth context/provider
    types/         shared TypeScript interfaces mirroring backend schemas
```

## Design Notes

- **Master configuration** (loan types, duration limits, approval fee limits, repayment
  frequencies, penalty rates) is stored in the database and editable by ADMIN. Changing it only
  affects new applications/approvals; every `Loan`, `LoanFee`, and `RepaymentSchedule` freezes the
  values that were actually used at the time it was created.
- **Money** is `Decimal` end-to-end (Python `Decimal`, MySQL `DECIMAL`, TypeScript `string`) -
  never `float`/`double`.
- **The Virtual Account has no external funding endpoint** (none is specified in the system's
  scope, since there is no real bank integration). A new client's account opens with a fixed
  demo balance so approval fees, EMIs, and prepayments can be exercised end-to-end. See
  `app/services/account_service.py`.
- **No background scheduler** (Celery/cron are out of scope). Overdue detection and penalty
  accrual run lazily whenever a loan is read or paid against - see `app/services/penalty_service.py`.
