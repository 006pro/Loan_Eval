import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import * as loanApplicationsService from "../../services/loanApplications";
import * as loansService from "../../services/loans";
import * as accountsService from "../../services/accounts";
import { StatusBadge } from "../../components/StatusBadge";
import { formatCurrency, formatDate } from "../../utils/format";
import type { Loan, LoanApplication, VirtualAccount } from "../../types";

export function DashboardPage() {
  const [applications, setApplications] = useState<LoanApplication[]>([]);
  const [loans, setLoans] = useState<Loan[]>([]);
  const [account, setAccount] = useState<VirtualAccount | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      loanApplicationsService.listMyApplications(),
      loansService.listMyLoans(),
      accountsService.getMyAccount(),
    ])
      .then(([apps, loanList, acct]) => {
        setApplications(apps);
        setLoans(loanList);
        setAccount(acct);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="empty-state">Loading dashboard...</div>;

  const activeLoans = loans.filter((loan) => loan.status === "ACTIVE" || loan.status === "OVERDUE");
  const pendingApplications = applications.filter(
    (app) => app.status === "SUBMITTED" || app.status === "UNDER_REVIEW"
  );
  const outstandingPrincipal = activeLoans.reduce((sum, loan) => sum + Number(loan.outstanding_principal), 0);

  return (
    <div>
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Overview of your loans, applications, and Virtual Account.</p>
      </div>

      <div className="summary-row">
        <div className="summary-item">
          <div className="label">Active Loans</div>
          <div className="value">{activeLoans.length}</div>
        </div>
        <div className="summary-item">
          <div className="label">Pending Applications</div>
          <div className="value">{pendingApplications.length}</div>
        </div>
        <div className="summary-item">
          <div className="label">Outstanding Principal</div>
          <div className="value">{formatCurrency(outstandingPrincipal)}</div>
        </div>
        <div className="summary-item">
          <div className="label">Virtual Account Balance</div>
          <div className="value">{account ? formatCurrency(account.balance) : "-"}</div>
        </div>
      </div>

      <div className="panel">
        <div className="panel-header">
          <h2>Recent Applications</h2>
          <Link to="/applications">View all</Link>
        </div>
        {applications.length === 0 ? (
          <div className="empty-state">No loan applications yet.</div>
        ) : (
          <div className="table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Loan Type</th>
                  <th>Amount</th>
                  <th>Status</th>
                  <th>Submitted</th>
                </tr>
              </thead>
              <tbody>
                {applications.slice(0, 5).map((app) => (
                  <tr key={app.id}>
                    <td>
                      <Link to={`/applications/${app.id}`}>{app.loan_type_name}</Link>
                    </td>
                    <td>{formatCurrency(app.requested_amount)}</td>
                    <td>
                      <StatusBadge status={app.status} />
                    </td>
                    <td>{formatDate(app.submitted_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="panel">
        <div className="panel-header">
          <h2>My Loans</h2>
          <Link to="/loans">View all</Link>
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
                  <th>Outstanding Principal</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {loans.slice(0, 5).map((loan) => (
                  <tr key={loan.id}>
                    <td>
                      <Link to={`/loans/${loan.id}`}>{loan.loan_type_name}</Link>
                    </td>
                    <td>{formatCurrency(loan.approved_amount)}</td>
                    <td>{formatCurrency(loan.outstanding_principal)}</td>
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
