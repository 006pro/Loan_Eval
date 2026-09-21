import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import * as adminService from "../../../services/admin";
import { ApiError } from "../../../services/api";

export function DurationRulesTab() {
  const [minimum, setMinimum] = useState("");
  const [maximum, setMaximum] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    adminService
      .getDurationRule()
      .then((rule) => {
        setMinimum(String(rule.minimum_months));
        setMaximum(String(rule.maximum_months));
      })
      .finally(() => setLoading(false));
  }, []);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setSuccess(false);
    setSaving(true);
    try {
      const updated = await adminService.updateDurationRule({
        minimum_months: Number(minimum),
        maximum_months: Number(maximum),
      });
      setMinimum(String(updated.minimum_months));
      setMaximum(String(updated.maximum_months));
      setSuccess(true);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Unable to update duration rule");
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <div className="empty-state">Loading duration rule...</div>;

  return (
    <div>
      <p className="field-hint">
        Controls the minimum and maximum loan duration clients may request. Existing loans keep the duration
        they were approved with.
      </p>
      {error && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">Duration rule updated.</div>}
      <form onSubmit={handleSubmit} noValidate>
        <div className="form-row">
          <div className="field">
            <label htmlFor="minimum_duration">Minimum Duration (months)</label>
            <input
              id="minimum_duration"
              type="number"
              min={1}
              required
              value={minimum}
              onChange={(e) => setMinimum(e.target.value)}
            />
          </div>
          <div className="field">
            <label htmlFor="maximum_duration">Maximum Duration (months)</label>
            <input
              id="maximum_duration"
              type="number"
              min={1}
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
