import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import * as adminService from "../../services/admin";
import { ApiError } from "../../services/api";
import { StatusBadge } from "../../components/StatusBadge";
import { formatCurrency, formatDateTime } from "../../utils/format";
import type { AdminLoanApplication } from "../../types";

export function ApplicationDetailsPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const applicationId = Number(id);

  const [application, setApplication] = useState<AdminLoanApplication | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [approvedAmount, setApprovedAmount] = useState("");
  const [feePercent, setFeePercent] = useState("");
  const [creditScore, setCreditScore] = useState("");
  const [remarks, setRemarks] = useState("");
  const [rejectionReason, setRejectionReason] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    adminService
      .getApplication(applicationId)
      .then((app) => {
        setApplication(app);
        setApprovedAmount(app.requested_amount);
        setCreditScore(app.client.credit_score !== null ? String(app.client.credit_score) : "");
      })
      .catch(() => setError("Loan application not found."))
      .finally(() => setLoading(false));
  }, [applicationId]);

  const estimatedFeeAmount =
    approvedAmount && feePercent
      ? (Number(approvedAmount) * Number(feePercent)) / 100
      : null;

  async function handleApprove(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await adminService.approveApplication(applicationId, {
        approved_amount: approvedAmount,
        approval_fee_percent: feePercent,
        credit_score: creditScore ? Number(creditScore) : undefined,
        remarks: remarks || undefined,
      });
      navigate(`/admin/loans`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Unable to approve application");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleReject(event: FormEvent) {
    event.preventDefault();
    if (!rejectionReason.trim()) {
      setError("A rejection reason is required.");
      return;
    }
    setError(null);
    setSubmitting(true);
    try {
      const updated = await adminService.rejectApplication(applicationId, {
        rejection_reason: rejectionReason,
        credit_score: creditScore ? Number(creditScore) : undefined,
        remarks: remarks || undefined,
      });
      setApplication(updated);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Unable to reject application");
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) return <div className="empty-state">Loading application...</div>;
  if (!application) return <div className="alert alert-error">{error ?? "Not found"}</div>;

  const canEvaluate = application.status === "SUBMITTED" || application.status === "UNDER_REVIEW";

  return (
    <div>
      <div className="page-header">
        <h1>Application #{application.id}</h1>
        <p>
          <Link to="/admin/applications">Back to Loan Applications</Link>
        </p>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      <div className="panel">
        <div className="panel-header">
          <h2>Client</h2>
          <StatusBadge status={application.status} />
        </div>
        <div className="summary-row">
          <div className="summary-item">
            <div className="label">Name</div>
            <div className="value">{application.client.name}</div>
          </div>
          <div className="summary-item">
            <div className="label">Phone</div>
            <div className="value">{application.client.phone ?? "-"}</div>
          </div>
          <div className="summary-item">
            <div className="label">Monthly Income</div>
            <div className="value">
              {application.client.monthly_income ? formatCurrency(application.client.monthly_income) : "-"}
            </div>
          </div>
          <div className="summary-item">
            <div className="label">Existing Loans</div>
            <div className="value">{application.client.existing_loans}</div>
          </div>
          <div className="summary-item">
            <div className="label">Credit Score</div>
            <div className="value">{application.client.credit_score ?? "-"}</div>
          </div>
        </div>
      </div>

      <div className="panel">
        <h2>Requested Loan</h2>
        <div className="summary-row">
          <div className="summary-item">
            <div className="label">Loan Type</div>
            <div className="value">{application.loan_type_name}</div>
          </div>
          <div className="summary-item">
            <div className="label">Interest Rate</div>
            <div className="value">{application.interest_rate}%</div>
          </div>
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
      </div>

      {application.status === "REJECTED" && (
        <div className="alert alert-error">
          <strong>Rejected</strong>
          <p style={{ margin: "0.4rem 0 0" }}>{application.rejection_reason}</p>
        </div>
      )}

      {application.status === "APPROVED" && (
        <div className="alert alert-success">This application has been approved.</div>
      )}

      {canEvaluate && (
        <div className="panel">
          <h2>Approve</h2>
          <form onSubmit={handleApprove} noValidate>
            <div className="form-row">
              <div className="field">
                <label htmlFor="approved_amount">Approved Amount</label>
                <input
                  id="approved_amount"
                  type="number"
                  required
                  min={0}
                  step="0.01"
                  value={approvedAmount}
                  onChange={(e) => setApprovedAmount(e.target.value)}
                />
              </div>
              <div className="field">
                <label htmlFor="fee_percent">Approval Fee %</label>
                <input
                  id="fee_percent"
                  type="number"
                  required
                  min={0}
                  max={100}
                  step="0.01"
                  value={feePercent}
                  onChange={(e) => setFeePercent(e.target.value)}
                />
              </div>
            </div>
            <div className="form-row">
              <div className="field">
                <label htmlFor="credit_score">Reviewed Credit Score</label>
                <input
                  id="credit_score"
                  type="number"
                  min={300}
                  max={900}
                  value={creditScore}
                  onChange={(e) => setCreditScore(e.target.value)}
                />
              </div>
              <div className="field">
                <label>Calculated Fee Amount</label>
                <input value={estimatedFeeAmount !== null ? formatCurrency(estimatedFeeAmount) : ""} disabled />
              </div>
            </div>
            <div className="field">
              <label htmlFor="remarks">Remarks (optional)</label>
              <textarea id="remarks" rows={2} value={remarks} onChange={(e) => setRemarks(e.target.value)} />
            </div>
            <div className="form-actions">
              <button type="submit" className="btn" disabled={submitting}>
                {submitting ? "Approving..." : "Approve Application"}
              </button>
            </div>
          </form>
        </div>
      )}

      {canEvaluate && (
        <div className="panel">
          <h2>Reject</h2>
          <form onSubmit={handleReject} noValidate>
            <div className="field">
              <label htmlFor="rejection_reason">Rejection Reason</label>
              <textarea
                id="rejection_reason"
                required
                rows={3}
                value={rejectionReason}
                onChange={(e) => setRejectionReason(e.target.value)}
              />
            </div>
            <div className="form-actions">
              <button type="submit" className="btn btn-danger" disabled={submitting}>
                {submitting ? "Rejecting..." : "Reject Application"}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
