import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import * as adminService from "../../services/admin";
import { StatusBadge } from "../../components/StatusBadge";
import { formatCurrency, formatDate } from "../../utils/format";
import type { AdminLoanApplication, Loan } from "../../types";

export function AdminDashboardPage() {
  const [applications, setApplications] = useState<AdminLoanApplication[]>([]);
  const [loans, setLoans] = useState<Loan[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([adminService.listApplications(), adminService.listLoans()])
      .then(([apps, loanList]) => {
        setApplications(apps);
        setLoans(loanList);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="empty-state">Loading dashboard...</div>;

  const pending = applications.filter((a) => a.status === "SUBMITTED" || a.status === "UNDER_REVIEW");
  const activeLoans = loans.filter((l) => l.status === "ACTIVE" || l.status === "OVERDUE");
  const overdueLoans = loans.filter((l) => l.status === "OVERDUE");
  const outstanding = activeLoans.reduce((sum, l) => sum + Number(l.outstanding_principal), 0);

  return (
    <div>
      <div className="page-header">
        <h1>Admin Dashboard</h1>
        <p>Loan application review queue and portfolio overview.</p>
      </div>

      <div className="summary-row">
        <div className="summary-item">
          <div className="label">Pending Applications</div>
          <div className="value">{pending.length}</div>
        </div>
        <div className="summary-item">
          <div className="label">Active Loans</div>
          <div className="value">{activeLoans.length}</div>
        </div>
        <div className="summary-item">
          <div className="label">Overdue Loans</div>
          <div className="value">{overdueLoans.length}</div>
        </div>
        <div className="summary-item">
          <div className="label">Outstanding Principal</div>
          <div className="value">{formatCurrency(outstanding)}</div>
        </div>
      </div>

      <div className="panel">
        <div className="panel-header">
          <h2>Applications Awaiting Review</h2>
          <Link to="/admin/applications">View all</Link>
        </div>
        {pending.length === 0 ? (
          <div className="empty-state">No applications are awaiting review.</div>
        ) : (
          <div className="table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Client</th>
                  <th>Loan Type</th>
                  <th>Amount</th>
                  <th>Submitted</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {pending.slice(0, 8).map((app) => (
                  <tr key={app.id}>
                    <td>{app.client.name}</td>
                    <td>{app.loan_type_name}</td>
                    <td>{formatCurrency(app.requested_amount)}</td>
                    <td>{formatDate(app.submitted_at)}</td>
                    <td>
                      <Link to={`/admin/applications/${app.id}`}>Review</Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="panel">
        <div className="panel-header">
          <h2>Loans</h2>
          <Link to="/admin/loans">View all</Link>
        </div>
        {loans.length === 0 ? (
          <div className="empty-state">No loans yet.</div>
        ) : (
          <div className="table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Loan Type</th>
                  <th>Approved Amount</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {loans.slice(0, 8).map((loan) => (
                  <tr key={loan.id}>
                    <td>
                      <Link to={`/admin/loans/${loan.id}`}>{loan.loan_type_name}</Link>
                    </td>
                    <td>{formatCurrency(loan.approved_amount)}</td>
                    <td>
                      <StatusBadge status={loan.status} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
