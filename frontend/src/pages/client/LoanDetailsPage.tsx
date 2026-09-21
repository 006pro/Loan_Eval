import { useCallback, useEffect, useState } from "react";
import type { FormEvent } from "react";
import { Link, useParams } from "react-router-dom";
import * as loansService from "../../services/loans";
import { ApiError } from "../../services/api";
import { StatusBadge } from "../../components/StatusBadge";
import { formatCurrency, formatDate } from "../../utils/format";
import type { Loan, Payment, RepaymentScheduleRow } from "../../types";

export function LoanDetailsPage() {
  const { id } = useParams();
  const loanId = Number(id);

  const [loan, setLoan] = useState<Loan | null>(null);
  const [schedule, setSchedule] = useState<RepaymentScheduleRow[]>([]);
  const [payments, setPayments] = useState<Payment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [prepaymentAmount, setPrepaymentAmount] = useState("");

  const load = useCallback(async () => {
    const loanData = await loansService.getLoan(loanId);
    setLoan(loanData);
    if (loanData.status !== "PENDING_FEE") {
      const [scheduleData, paymentsData] = await Promise.all([
        loansService.getSchedule(loanId),
        loansService.listPayments(loanId),
      ]);
      setSchedule(scheduleData);
      setPayments(paymentsData);
    }
  }, [loanId]);

  useEffect(() => {
    setLoading(true);
    load()
      .catch(() => setError("Loan not found."))
      .finally(() => setLoading(false));
  }, [load]);

  async function handlePayFee() {
    setBusy(true);
    setError(null);
    setNotice(null);
    try {
      await loansService.payFee(loanId);
      setNotice("Approval fee paid. Loan is now active and the repayment schedule has been generated.");
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Unable to pay approval fee");
    } finally {
      setBusy(false);
    }
  }

  async function handlePayInstallment() {
    setBusy(true);
    setError(null);
    setNotice(null);
    try {
      const payment = await loansService.payInstallment(loanId);
      setNotice(`Installment paid: ${formatCurrency(payment.amount)}.`);
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Unable to pay installment");
    } finally {
      setBusy(false);
    }
  }

  async function handlePrepayment(event: FormEvent) {
    event.preventDefault();
    if (!prepaymentAmount) return;
    setBusy(true);
    setError(null);
    setNotice(null);
    try {
      await loansService.makePrepayment(loanId, prepaymentAmount);
      setNotice("Prepayment applied. Outstanding principal and remaining EMIs have been updated.");
      setPrepaymentAmount("");
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Unable to process prepayment");
    } finally {
      setBusy(false);
    }
  }

  if (loading) return <div className="empty-state">Loading loan...</div>;
  if (error && !loan) return <div className="alert alert-error">{error}</div>;
  if (!loan) return null;

  const nextInstallment = schedule.find((row) => row.status !== "PAID");
  const canPay = loan.status === "ACTIVE" || loan.status === "OVERDUE";

  return (
    <div>
      <div className="page-header">
        <h1>Loan #{loan.id}</h1>
        <p>
          <Link to="/loans">Back to My Loans</Link>
        </p>
      </div>

      {error && <div className="alert alert-error">{error}</div>}
      {notice && <div className="alert alert-success">{notice}</div>}

      <div className="panel">
        <div className="panel-header">
          <h2>{loan.loan_type_name}</h2>
          <StatusBadge status={loan.status} />
        </div>
        <div className="summary-row">
          <div className="summary-item">
            <div className="label">Approved Amount</div>
            <div className="value">{formatCurrency(loan.approved_amount)}</div>
          </div>
          <div className="summary-item">
            <div className="label">Interest Rate</div>
            <div className="value">{loan.interest_rate}%</div>
          </div>
          <div className="summary-item">
            <div className="label">Duration</div>
            <div className="value">{loan.duration_months} months</div>
          </div>
          <div className="summary-item">
            <div className="label">EMI Amount</div>
            <div className="value">{formatCurrency(loan.emi_amount)}</div>
          </div>
          <div className="summary-item">
            <div className="label">Outstanding Principal</div>
            <div className="value">{formatCurrency(loan.outstanding_principal)}</div>
          </div>
          <div className="summary-item">
            <div className="label">Next Payment</div>
            <div className="value">{nextInstallment ? formatDate(nextInstallment.due_date) : "-"}</div>
          </div>
        </div>
      </div>

      {loan.status === "PENDING_FEE" && loan.fee && (
        <div className="panel">
          <h2>Approval Fee</h2>
          <div className="summary-row">
            <div className="summary-item">
              <div className="label">Fee Percentage</div>
              <div className="value">{loan.fee.fee_percentage}%</div>
            </div>
            <div className="summary-item">
              <div className="label">Fee Amount</div>
              <div className="value">{formatCurrency(loan.fee.fee_amount)}</div>
            </div>
            <div className="summary-item">
              <div className="label">Status</div>
              <div className="value">
                <StatusBadge status={loan.fee.status} />
              </div>
            </div>
          </div>
          <p className="field-hint">
            The fee is debited from your Virtual Account. Once paid, the approved amount is credited and this
            loan becomes active.
          </p>
          <button type="button" className="btn" onClick={handlePayFee} disabled={busy}>
            {busy ? "Processing..." : "Pay Approval Fee"}
          </button>
        </div>
      )}

      {loan.status !== "PENDING_FEE" && (
        <>
          <div className="panel">
            <div className="panel-header">
              <h2>Repayment Schedule</h2>
              {canPay && (
                <button type="button" className="btn" onClick={handlePayInstallment} disabled={busy}>
                  {busy ? "Processing..." : "Pay Next Installment"}
                </button>
              )}
            </div>
            <div className="table-wrapper">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Due Date</th>
                    <th>Principal</th>
                    <th>Interest</th>
                    <th>Amount</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {schedule.map((row) => (
                    <tr key={row.id}>
                      <td>{row.installment_number}</td>
                      <td>{formatDate(row.due_date)}</td>
                      <td>{formatCurrency(row.scheduled_principal)}</td>
                      <td>{formatCurrency(row.scheduled_interest)}</td>
                      <td>{formatCurrency(row.scheduled_amount)}</td>
                      <td>
                        <StatusBadge status={row.status} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {canPay && (
            <div className="panel">
              <h2>Principal Prepayment</h2>
              <p className="field-hint">
                Reduces your outstanding principal immediately. The lower balance is reflected in your remaining
                installments starting from the next due date; past payments are not changed.
              </p>
              <form onSubmit={handlePrepayment} noValidate>
                <div className="field" style={{ maxWidth: 260 }}>
                  <label htmlFor="prepayment_amount">Prepayment Amount</label>
                  <input
                    id="prepayment_amount"
                    type="number"
                    min={0}
                    step="0.01"
                    required
                    value={prepaymentAmount}
                    onChange={(e) => setPrepaymentAmount(e.target.value)}
                  />
                </div>
                <button type="submit" className="btn btn-secondary" disabled={busy}>
                  {busy ? "Processing..." : "Make Prepayment"}
                </button>
              </form>
            </div>
          )}

          <div className="panel">
            <h2>Payment History</h2>
            {payments.length === 0 ? (
              <div className="empty-state">No payments recorded yet.</div>
            ) : (
              <div className="table-wrapper">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Amount</th>
                      <th>Principal</th>
                      <th>Interest</th>
                      <th>Penalty</th>
                    </tr>
                  </thead>
                  <tbody>
                    {payments.map((payment) => (
                      <tr key={payment.id}>
                        <td>{formatDate(payment.payment_date)}</td>
                        <td>{formatCurrency(payment.amount)}</td>
                        <td>{formatCurrency(payment.principal_amount)}</td>
                        <td>{formatCurrency(payment.interest_amount)}</td>
                        <td>{formatCurrency(payment.penalty_amount)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
