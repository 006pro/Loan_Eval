import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import * as loanApplicationsService from "../../services/loanApplications";
import { StatusBadge } from "../../components/StatusBadge";
import { formatCurrency, formatDateTime } from "../../utils/format";
import type { LoanApplication } from "../../types";

export function ApplicationDetailsPage() {
  const { id } = useParams();
  const [application, setApplication] = useState<LoanApplication | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    loanApplicationsService
      .getApplication(Number(id))
      .then(setApplication)
      .catch(() => setError("Loan application not found."))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="empty-state">Loading application...</div>;
  if (error || !application) return <div className="alert alert-error">{error ?? "Not found"}</div>;

  return (
    <div>
      <div className="page-header">
        <h1>Application #{application.id}</h1>
        <p>
          <Link to="/applications">Back to My Applications</Link>
        </p>
      </div>

      <div className="panel">
        <div className="panel-header">
          <h2>{application.loan_type_name}</h2>
          <StatusBadge status={application.status} />
        </div>
        <div className="summary-row">
          <div className="summary-item">
            <div className="label">Requested Amount</div>
            <div className="value">{formatCurrency(application.requested_amount)}</div>
          </div>
          <div className="summary-item">
            <div className="label">Duration</div>
            <div className="value">{application.requested_duration_months} months</div>
          </div>
          <div className="summary-item">
            <div className="label">Repayment Frequency</div>
            <div className="value">{application.requested_frequency}</div>
          </div>
          <div className="summary-item">
            <div className="label">Submitted</div>
            <div className="value">{formatDateTime(application.submitted_at)}</div>
          </div>
        </div>

        {application.status === "REJECTED" && (
          <div className="alert alert-error">
            <strong>Application Status: REJECTED</strong>
            <p style={{ margin: "0.4rem 0 0" }}>Reason: {application.rejection_reason}</p>
          </div>
        )}

        {application.status === "APPROVED" && (
          <div className="alert alert-success">
            This application has been approved. View it under <Link to="/loans">My Loans</Link> to pay the
            approval fee and activate the loan.
          </div>
        )}
      </div>
    </div>
  );
}
