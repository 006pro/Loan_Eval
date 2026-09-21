import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import * as loanApplicationsService from "../../services/loanApplications";
import { StatusBadge } from "../../components/StatusBadge";
import { formatCurrency, formatDate } from "../../utils/format";
import type { LoanApplication } from "../../types";

export function MyApplicationsPage() {
  const [applications, setApplications] = useState<LoanApplication[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loanApplicationsService.listMyApplications().then(setApplications).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="empty-state">Loading applications...</div>;

  return (
    <div>
      <div className="page-header">
        <h1>My Applications</h1>
        <p>Track the status of every loan application you have submitted.</p>
      </div>

      <div className="panel">
        {applications.length === 0 ? (
          <div className="empty-state">
            You have not submitted any loan applications yet. <Link to="/apply">Apply for a loan</Link>.
          </div>
        ) : (
          <div className="table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Loan Type</th>
                  <th>Amount</th>
                  <th>Duration</th>
                  <th>Frequency</th>
                  <th>Status</th>
                  <th>Submitted</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {applications.map((app) => (
                  <tr key={app.id}>
                    <td>{app.loan_type_name}</td>
                    <td>{formatCurrency(app.requested_amount)}</td>
                    <td>{app.requested_duration_months} months</td>
                    <td>{app.requested_frequency}</td>
                    <td>
                      <StatusBadge status={app.status} />
                    </td>
                    <td>{formatDate(app.submitted_at)}</td>
                    <td>
                      <Link to={`/applications/${app.id}`}>View</Link>
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
