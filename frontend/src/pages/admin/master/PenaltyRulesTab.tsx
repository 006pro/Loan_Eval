import { useEffect, useState } from "react";
import * as adminService from "../../../services/admin";
import { ApiError } from "../../../services/api";
import { formatFrequency } from "../../../utils/format";
import type { PenaltyRule } from "../../../types";

export function PenaltyRulesTab() {
  const [rules, setRules] = useState<PenaltyRule[]>([]);
  const [rateDrafts, setRateDrafts] = useState<Record<number, string>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [savingId, setSavingId] = useState<number | null>(null);

  function refresh() {
    return adminService.listPenaltyRules().then((data) => {
      setRules(data);
      setRateDrafts(Object.fromEntries(data.map((rule) => [rule.id, rule.penalty_rate])));
    });
  }

  useEffect(() => {
    refresh().finally(() => setLoading(false));
  }, []);

  async function saveRate(rule: PenaltyRule) {
    setError(null);
    setSavingId(rule.id);
    try {
      await adminService.updatePenaltyRule(rule.id, rateDrafts[rule.id]);
      await refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Unable to update penalty rule");
    } finally {
      setSavingId(null);
    }
  }

  async function toggleActive(rule: PenaltyRule) {
    setError(null);
    try {
      await adminService.updatePenaltyRule(rule.id, rule.penalty_rate, !rule.is_active);
      await refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Unable to update penalty rule");
    }
  }

  if (loading) return <div className="empty-state">Loading penalty rules...</div>;

  return (
    <div>
      <p className="field-hint">
        The penalty rate applies per day (MONTHLY) or per week (all other frequencies) on the overdue
        installment amount.
      </p>
      {error && <div className="alert alert-error">{error}</div>}
      <div className="table-wrapper">
        <table className="data-table">
          <thead>
            <tr>
              <th>Repayment Frequency</th>
              <th>Calculation Frequency</th>
              <th>Penalty Rate %</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {rules.map((rule) => (
              <tr key={rule.id}>
                <td>{formatFrequency(rule.repayment_frequency)}</td>
                <td>{rule.calculation_frequency}</td>
                <td>
                  <input
                    type="number"
                    min={0}
                    max={100}
                    step="0.01"
                    style={{ width: "90px" }}
                    value={rateDrafts[rule.id] ?? ""}
                    onChange={(e) => setRateDrafts({ ...rateDrafts, [rule.id]: e.target.value })}
                  />
                </td>
                <td>{rule.is_active ? "Active" : "Inactive"}</td>
                <td style={{ display: "flex", gap: "0.4rem" }}>
                  <button
                    type="button"
                    className="btn btn-small"
                    disabled={savingId === rule.id}
                    onClick={() => saveRate(rule)}
                  >
                    Save
                  </button>
                  <button
                    type="button"
                    className="btn btn-secondary btn-small"
                    onClick={() => toggleActive(rule)}
                  >
                    {rule.is_active ? "Deactivate" : "Activate"}
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
