import { useEffect, useState } from "react";
import * as adminService from "../../../services/admin";
import { ApiError } from "../../../services/api";
import { formatFrequency } from "../../../utils/format";
import type { RepaymentFrequency } from "../../../types";

export function RepaymentFrequenciesTab() {
  const [frequencies, setFrequencies] = useState<RepaymentFrequency[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  function refresh() {
    return adminService.listRepaymentFrequencies().then(setFrequencies);
  }

  useEffect(() => {
    refresh().finally(() => setLoading(false));
  }, []);

  async function toggle(frequency: RepaymentFrequency) {
    setError(null);
    try {
      await adminService.updateRepaymentFrequency(frequency.id, !frequency.is_active);
      await refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Unable to update repayment frequency");
    }
  }

  if (loading) return <div className="empty-state">Loading repayment frequencies...</div>;

  return (
    <div>
      <p className="field-hint">
        Only active frequencies are offered to clients on the loan application form.
      </p>
      {error && <div className="alert alert-error">{error}</div>}
      <div className="table-wrapper">
        <table className="data-table">
          <thead>
            <tr>
              <th>Frequency</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {frequencies.map((freq) => (
              <tr key={freq.id}>
                <td>{formatFrequency(freq.code)}</td>
                <td>{freq.is_active ? "Active" : "Inactive"}</td>
                <td>
                  <button type="button" className="btn btn-secondary btn-small" onClick={() => toggle(freq)}>
                    {freq.is_active ? "Deactivate" : "Activate"}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
