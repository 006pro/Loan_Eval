import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import * as adminService from "../../services/admin";
import { ApiError } from "../../services/api";
import { formatDateTime } from "../../utils/format";
import type { AdminUser } from "../../types";

const EMPTY_FORM = { email: "", password: "", name: "", employee_id: "" };

export function AdminUsersPage() {
  const [admins, setAdmins] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);

  function refresh() {
    return adminService.listAdmins().then(setAdmins);
  }

  useEffect(() => {
    refresh().finally(() => setLoading(false));
  }, []);

  function startCreate() {
    setForm(EMPTY_FORM);
    setError(null);
    setShowForm(true);
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setSaving(true);
    try {
      await adminService.createAdmin(form);
      setShowForm(false);
      await refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Unable to create admin");
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <div className="empty-state">Loading admins...</div>;

  return (
    <div>
      <h2>Admin Users</h2>
      {error && <div className="alert alert-error">{error}</div>}

      <div className="table-wrapper">
        <table className="data-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Employee ID</th>
              <th>Created</th>
            </tr>
          </thead>
          <tbody>
            {admins.map((admin) => (
              <tr key={admin.id}>
                <td>{admin.name}</td>
                <td>{admin.email}</td>
                <td>{admin.employee_id}</td>
                <td>{formatDateTime(admin.created_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="form-actions">
        <button type="button" className="btn" onClick={startCreate}>
          Add Admin
        </button>
      </div>

      {showForm && (
        <div className="panel" style={{ marginTop: "1rem" }}>
          <h3>New Admin</h3>
          <form onSubmit={handleSubmit} noValidate>
            <div className="form-row">
              <div className="field">
                <label htmlFor="admin_name">Name</label>
                <input
                  id="admin_name"
                  required
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                />
              </div>
              <div className="field">
                <label htmlFor="admin_employee_id">Employee ID</label>
                <input
                  id="admin_employee_id"
                  required
                  value={form.employee_id}
                  onChange={(e) => setForm({ ...form, employee_id: e.target.value })}
                />
              </div>
            </div>
            <div className="form-row">
              <div className="field">
                <label htmlFor="admin_email">Email</label>
                <input
                  id="admin_email"
                  type="email"
                  required
                  value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                  autoComplete="off"
                />
              </div>
              <div className="field">
                <label htmlFor="admin_password">Password</label>
                <input
                  id="admin_password"
                  type="password"
                  required
                  minLength={8}
                  value={form.password}
                  onChange={(e) => setForm({ ...form, password: e.target.value })}
                  autoComplete="new-password"
                />
              </div>
            </div>
            <div className="form-actions">
              <button type="submit" className="btn" disabled={saving}>
                {saving ? "Creating..." : "Create Admin"}
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
