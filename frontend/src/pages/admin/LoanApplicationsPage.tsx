import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import * as adminService from "../../services/admin";
import { StatusBadge } from "../../components/StatusBadge";
import { formatCurrency, formatDate } from "../../utils/format";
import type { AdminLoanApplication, ApplicationStatus } from "../../types";

const STATUS_FILTERS: { label: string; value: ApplicationStatus | "ALL" }[] = [
  { label: "All", value: "ALL" },
  { label: "Submitted", value: "SUBMITTED" },
  { label: "Under Review", value: "UNDER_REVIEW" },
  { label: "Approved", value: "APPROVED" },
  { label: "Rejected", value: "REJECTED" },
];

export function LoanApplicationsPage() {
  const [applications, setApplications] = useState<AdminLoanApplication[]>([]);
  const [statusFilter, setStatusFilter] = useState<ApplicationStatus | "ALL">("ALL");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    adminService
      .listApplications(statusFilter === "ALL" ? undefined : statusFilter)
      .then(setApplications)
      .finally(() => setLoading(false));
  }, [statusFilter]);

  return (
    <div>
      <div className="page-header">
        <h1>Loan Applications</h1>
        <p>Review client applications, approve with fee terms, or reject with a reason.</p>
      </div>

      <div className="panel">
        <div className="panel-header">
          <h2>Applications</h2>
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value as ApplicationStatus | "ALL")}>
            {STATUS_FILTERS.map((filter) => (
              <option key={filter.value} value={filter.value}>
                {filter.label}
              </option>
            ))}
          </select>
        </div>

        {loading ? (
          <div className="empty-state">Loading applications...</div>
        ) : applications.length === 0 ? (
          <div className="empty-state">No applications match this filter.</div>
        ) : (
          <div className="table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Client</th>
                  <th>Loan Type</th>
                  <th>Amount</th>
                  <th>Duration</th>
                  <th>Status</th>
                  <th>Submitted</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {applications.map((app) => (
                  <tr key={app.id}>
                    <td>{app.client.name}</td>
                    <td>{app.loan_type_name}</td>
                    <td>{formatCurrency(app.requested_amount)}</td>
                    <td>{app.requested_duration_months} months</td>
                    <td>
                      <StatusBadge status={app.status} />
                    </td>
                    <td>{formatDate(app.submitted_at)}</td>
                    <td>
                      <Link to={`/admin/applications/${app.id}`}>View</Link>
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
