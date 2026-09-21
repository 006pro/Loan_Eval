import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import * as adminService from "../../services/admin";
import { StatusBadge } from "../../components/StatusBadge";
import { formatCurrency, formatDate } from "../../utils/format";
import type { Loan, RepaymentScheduleRow } from "../../types";

export function LoanDetailsPage() {
  const { id } = useParams();
  const loanId = Number(id);

  const [loan, setLoan] = useState<Loan | null>(null);
  const [schedule, setSchedule] = useState<RepaymentScheduleRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([adminService.getLoan(loanId), adminService.getLoanSchedule(loanId)])
      .then(([loanData, scheduleData]) => {
        setLoan(loanData);
        setSchedule(scheduleData);
      })
      .catch(() => setError("Loan not found."))
      .finally(() => setLoading(false));
  }, [loanId]);

  if (loading) return <div className="empty-state">Loading loan...</div>;
  if (error || !loan) return <div className="alert alert-error">{error ?? "Not found"}</div>;

  return (
    <div>
      <div className="page-header">
        <h1>Loan #{loan.id}</h1>
        <p>
          <Link to="/admin/loans">Back to Loans</Link>
        </p>
      </div>

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
        </div>
      </div>

      {loan.fee && (
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
        </div>
      )}

      {schedule.length > 0 && (
        <div className="panel">
          <h2>Repayment Schedule</h2>
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
      )}
    </div>
  );
}
