import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import * as adminService from "../../../services/admin";
import { ApiError } from "../../../services/api";
import { formatCurrency } from "../../../utils/format";
import type { LoanType } from "../../../types";

const EMPTY_FORM = { name: "", description: "", interest_rate: "", min_amount: "", max_amount: "" };

export function LoanTypesTab() {
  const [loanTypes, setLoanTypes] = useState<LoanType[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);

  function refresh() {
    return adminService.listLoanTypes().then(setLoanTypes);
  }

  useEffect(() => {
    refresh().finally(() => setLoading(false));
  }, []);

  function startCreate() {
    setEditingId(null);
    setForm(EMPTY_FORM);
    setShowForm(true);
  }

  function startEdit(loanType: LoanType) {
    setEditingId(loanType.id);
    setForm({
      name: loanType.name,
      description: loanType.description ?? "",
      interest_rate: loanType.interest_rate,
      min_amount: loanType.min_amount,
      max_amount: loanType.max_amount,
    });
    setShowForm(true);
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setSaving(true);
    try {
      if (editingId !== null) {
        await adminService.updateLoanType(editingId, {
          name: form.name,
          description: form.description || undefined,
          interest_rate: form.interest_rate,
          min_amount: form.min_amount,
          max_amount: form.max_amount,
        });
      } else {
        await adminService.createLoanType({
          name: form.name,
          description: form.description || undefined,
          interest_rate: form.interest_rate,
          min_amount: form.min_amount,
          max_amount: form.max_amount,
        });
      }
      setShowForm(false);
      await refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Unable to save loan type");
    } finally {
      setSaving(false);
    }
  }

  async function toggleActive(loanType: LoanType) {
    setError(null);
    try {
      await adminService.updateLoanType(loanType.id, { is_active: !loanType.is_active });
      await refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Unable to update loan type");
    }
  }

  if (loading) return <div className="empty-state">Loading loan types...</div>;

  return (
    <div>
      {error && <div className="alert alert-error">{error}</div>}

      <div className="table-wrapper">
        <table className="data-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Interest Rate</th>
              <th>Minimum Amount</th>
              <th>Maximum Amount</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {loanTypes.map((lt) => (
              <tr key={lt.id}>
                <td>{lt.name}</td>
                <td>{lt.interest_rate}%</td>
                <td>{formatCurrency(lt.min_amount)}</td>
                <td>{formatCurrency(lt.max_amount)}</td>
                <td>{lt.is_active ? "Active" : "Inactive"}</td>
                <td style={{ display: "flex", gap: "0.4rem" }}>
                  <button type="button" className="btn btn-secondary btn-small" onClick={() => startEdit(lt)}>
                    Edit
                  </button>
                  <button type="button" className="btn btn-secondary btn-small" onClick={() => toggleActive(lt)}>
                    {lt.is_active ? "Deactivate" : "Activate"}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="form-actions">
        <button type="button" className="btn" onClick={startCreate}>
          Add Loan Type
        </button>
      </div>

      {showForm && (
        <div className="panel" style={{ marginTop: "1rem" }}>
          <h3>{editingId !== null ? "Edit Loan Type" : "New Loan Type"}</h3>
          <form onSubmit={handleSubmit} noValidate>
            <div className="form-row">
              <div className="field">
                <label htmlFor="lt_name">Name</label>
                <input
                  id="lt_name"
                  required
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                />
              </div>
              <div className="field">
                <label htmlFor="lt_rate">Interest Rate %</label>
                <input
                  id="lt_rate"
                  type="number"
                  min={0}
                  max={100}
                  step="0.01"
                  required
                  value={form.interest_rate}
                  onChange={(e) => setForm({ ...form, interest_rate: e.target.value })}
                />
              </div>
            </div>
            <div className="field">
              <label htmlFor="lt_description">Description</label>
              <input
                id="lt_description"
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
              />
            </div>
            <div className="form-row">
              <div className="field">
                <label htmlFor="lt_min">Minimum Amount</label>
                <input
                  id="lt_min"
                  type="number"
                  min={0}
                  step="0.01"
                  required
                  value={form.min_amount}
                  onChange={(e) => setForm({ ...form, min_amount: e.target.value })}
                />
              </div>
              <div className="field">
                <label htmlFor="lt_max">Maximum Amount</label>
                <input
                  id="lt_max"
                  type="number"
                  min={0}
                  step="0.01"
                  required
                  value={form.max_amount}
                  onChange={(e) => setForm({ ...form, max_amount: e.target.value })}
                />
              </div>
            </div>
            <div className="form-actions">
              <button type="submit" className="btn" disabled={saving}>
                {saving ? "Saving..." : "Save Loan Type"}
              </button>
              <button type="button" className="btn btn-secondary" onClick={() => setShowForm(false)}>
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
