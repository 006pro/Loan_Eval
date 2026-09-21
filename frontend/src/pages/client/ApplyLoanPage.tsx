import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import * as loanTypesService from "../../services/loanTypes";
import * as loanApplicationsService from "../../services/loanApplications";
import { ApiError } from "../../services/api";
import { formatCurrency, formatFrequency } from "../../utils/format";
import type { ApplicationConfig, LoanApplicationPreview, LoanType, RepaymentFrequencyCode } from "../../types";

export function ApplyLoanPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const [loanTypes, setLoanTypes] = useState<LoanType[]>([]);
  const [config, setConfig] = useState<ApplicationConfig | null>(null);
  const [loanTypeId, setLoanTypeId] = useState(searchParams.get("loan_type_id") ?? "");
  const [amount, setAmount] = useState("");
  const [duration, setDuration] = useState("");
  const [frequency, setFrequency] = useState<RepaymentFrequencyCode | "">("");

  const [preview, setPreview] = useState<LoanApplicationPreview | null>(null);
  const [previewing, setPreviewing] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([loanTypesService.listActiveLoanTypes(), loanApplicationsService.getApplicationConfig()])
      .then(([types, cfg]) => {
        setLoanTypes(types);
        setConfig(cfg);
        if (!frequency && cfg.active_repayment_frequencies.length > 0) {
          setFrequency(cfg.active_repayment_frequencies[0]);
        }
      })
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handlePreview() {
    if (!loanTypeId || !amount || !duration || !frequency) {
      setError("Fill in loan type, amount, duration, and frequency before previewing.");
      return;
    }
    setError(null);
    setPreviewing(true);
    setPreview(null);
    try {
      const result = await loanApplicationsService.previewApplication({
        loan_type_id: Number(loanTypeId),
        requested_amount: amount,
        requested_duration_months: Number(duration),
        requested_frequency: frequency,
      });
      setPreview(result);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Unable to calculate preview");
    } finally {
      setPreviewing(false);
    }
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!loanTypeId || !amount || !duration || !frequency) {
      setError("Fill in loan type, amount, duration, and frequency.");
      return;
    }
    setError(null);
    setSubmitting(true);
    try {
      const application = await loanApplicationsService.submitApplication({
        loan_type_id: Number(loanTypeId),
        requested_amount: amount,
        requested_duration_months: Number(duration),
        requested_frequency: frequency,
      });
      navigate(`/applications/${application.id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Unable to submit application");
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) return <div className="empty-state">Loading application form...</div>;

  const selectedLoanType = loanTypes.find((lt) => lt.id === Number(loanTypeId));

  return (
    <div>
      <div className="page-header">
        <h1>Apply for Loan</h1>
        <p>All calculations are performed by the server based on current Master configuration.</p>
      </div>

      <div className="panel">
        {error && <div className="alert alert-error">{error}</div>}
        <form onSubmit={handleSubmit} noValidate>
          <div className="field">
            <label htmlFor="loan_type">Loan Type</label>
            <select
              id="loan_type"
              required
              value={loanTypeId}
              onChange={(e) => {
                setLoanTypeId(e.target.value);
                setPreview(null);
              }}
            >
              <option value="">Select a loan type</option>
              {loanTypes.map((lt) => (
                <option key={lt.id} value={lt.id}>
                  {lt.name} ({lt.interest_rate}%)
                </option>
              ))}
            </select>
            {selectedLoanType && (
              <span className="field-hint">
                Amount range: {formatCurrency(selectedLoanType.min_amount)} - {formatCurrency(selectedLoanType.max_amount)}
              </span>
            )}
          </div>

          <div className="form-row">
            <div className="field">
              <label htmlFor="amount">Loan Amount</label>
              <input
                id="amount"
                type="number"
                required
                min={0}
                step="0.01"
                value={amount}
                onChange={(e) => {
                  setAmount(e.target.value);
                  setPreview(null);
                }}
              />
            </div>
            <div className="field">
              <label htmlFor="duration">Duration (months)</label>
              <input
                id="duration"
                type="number"
                required
                min={config?.minimum_duration_months ?? 1}
                max={config?.maximum_duration_months ?? 360}
                value={duration}
                onChange={(e) => {
                  setDuration(e.target.value);
                  setPreview(null);
                }}
              />
              {config && (
                <span className="field-hint">
                  Allowed range: {config.minimum_duration_months} - {config.maximum_duration_months} months
                </span>
              )}
            </div>
          </div>

          <div className="field">
            <label htmlFor="frequency">Repayment Frequency</label>
            <select
              id="frequency"
              required
              value={frequency}
              onChange={(e) => {
                setFrequency(e.target.value as RepaymentFrequencyCode);
                setPreview(null);
              }}
            >
              {config?.active_repayment_frequencies.map((code) => (
                <option key={code} value={code}>
                  {formatFrequency(code)}
                </option>
              ))}
            </select>
          </div>

          <div className="form-actions">
            <button type="button" className="btn btn-secondary" onClick={handlePreview} disabled={previewing}>
              {previewing ? "Calculating..." : "Preview Repayment"}
            </button>
            <button type="submit" className="btn" disabled={submitting}>
              {submitting ? "Submitting..." : "Submit Application"}
            </button>
          </div>
        </form>
      </div>

      {preview && (
        <div className="panel">
          <h2>Repayment Preview</h2>
          <div className="summary-row">
            <div className="summary-item">
              <div className="label">Interest Rate</div>
              <div className="value">{preview.interest_rate}%</div>
            </div>
            <div className="summary-item">
              <div className="label">Installment Amount</div>
              <div className="value">{formatCurrency(preview.estimated_installment_amount)}</div>
            </div>
            <div className="summary-item">
              <div className="label">Total Interest</div>
              <div className="value">{formatCurrency(preview.estimated_total_interest)}</div>
            </div>
            <div className="summary-item">
              <div className="label">Total Payable</div>
              <div className="value">{formatCurrency(preview.estimated_total_payable)}</div>
            </div>
          </div>
          <p className="field-hint">
            {preview.number_of_installments} installments, paid {formatFrequency(preview.repayment_frequency).toLowerCase()}.
          </p>
        </div>
      )}
    </div>
  );
}
