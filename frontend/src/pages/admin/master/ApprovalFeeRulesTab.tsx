import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import * as adminService from "../../../services/admin";
import { ApiError } from "../../../services/api";

export function ApprovalFeeRulesTab() {
  const [minimum, setMinimum] = useState("");
  const [maximum, setMaximum] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    adminService
      .getFeeRule()
      .then((rule) => {
        setMinimum(rule.minimum_fee_percent);
        setMaximum(rule.maximum_fee_percent);
      })
      .finally(() => setLoading(false));
  }, []);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setSuccess(false);
    setSaving(true);
    try {
      const updated = await adminService.updateFeeRule({
        minimum_fee_percent: minimum,
        maximum_fee_percent: maximum,
      });
      setMinimum(updated.minimum_fee_percent);
      setMaximum(updated.maximum_fee_percent);
      setSuccess(true);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Unable to update approval fee rule");
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <div className="empty-state">Loading approval fee rule...</div>;

  return (
    <div>
      <p className="field-hint">
        Controls the allowed approval fee percentage range. Applied when an admin approves an application;
        already-approved loans keep the fee percentage used at the time.
      </p>
      {error && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">Approval fee rule updated.</div>}
      <form onSubmit={handleSubmit} noValidate>
        <div className="form-row">
          <div className="field">
            <label htmlFor="minimum_fee">Minimum Fee %</label>
            <input
              id="minimum_fee"
              type="number"
              min={0}
              max={100}
              step="0.01"
              required
              value={minimum}
              onChange={(e) => setMinimum(e.target.value)}
            />
          </div>
          <div className="field">
            <label htmlFor="maximum_fee">Maximum Fee %</label>
            <input
              id="maximum_fee"
              type="number"
              min={0}
              max={100}
              step="0.01"
              required
              value={maximum}
              onChange={(e) => setMaximum(e.target.value)}
            />
          </div>
        </div>
        <div className="form-actions">
          <button type="submit" className="btn" disabled={saving}>
            {saving ? "Saving..." : "Save Changes"}
          </button>
        </div>
      </form>
    </div>
  );
}
