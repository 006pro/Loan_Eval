import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import * as clientsService from "../../services/clients";
import { ApiError } from "../../services/api";
import type { ClientProfile } from "../../types";

export function ProfilePage() {
  const [profile, setProfile] = useState<ClientProfile | null>(null);
  const [form, setForm] = useState({
    name: "",
    phone: "",
    address: "",
    date_of_birth: "",
    employment: "",
    monthly_income: "",
    yearly_income: "",
    existing_loans: "0",
    bank_account_number: "",
    credit_score: "",
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    clientsService
      .getMyProfile()
      .then((data) => {
        setProfile(data);
        setForm({
          name: data.name,
          phone: data.phone ?? "",
          address: data.address ?? "",
          date_of_birth: data.date_of_birth ?? "",
          employment: data.employment ?? "",
          monthly_income: data.monthly_income ?? "",
          yearly_income: data.yearly_income ?? "",
          existing_loans: String(data.existing_loans),
          bank_account_number: data.bank_account_number ?? "",
          credit_score: data.credit_score !== null ? String(data.credit_score) : "",
        });
      })
      .finally(() => setLoading(false));
  }, []);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setSuccess(false);
    setSaving(true);
    try {
      const updated = await clientsService.updateMyProfile({
        name: form.name,
        phone: form.phone || undefined,
        address: form.address || undefined,
        date_of_birth: form.date_of_birth || undefined,
        employment: form.employment || undefined,
        monthly_income: form.monthly_income || undefined,
        yearly_income: form.yearly_income || undefined,
        existing_loans: form.existing_loans ? Number(form.existing_loans) : undefined,
        bank_account_number: form.bank_account_number || undefined,
        credit_score: form.credit_score ? Number(form.credit_score) : undefined,
      });
      setProfile(updated);
      setSuccess(true);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Unable to update profile");
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <div className="empty-state">Loading profile...</div>;

  return (
    <div>
      <div className="page-header">
        <h1>Profile</h1>
        <p>Keep your details current. A complete profile is required to apply for a loan.</p>
      </div>

      <div className="panel">
        {error && <div className="alert alert-error">{error}</div>}
        {success && <div className="alert alert-success">Profile updated successfully.</div>}
        <form onSubmit={handleSubmit} noValidate>
          <div className="form-row">
            <div className="field">
              <label htmlFor="name">Full Name</label>
              <input
                id="name"
                required
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
              />
            </div>
            <div className="field">
              <label htmlFor="email">Email</label>
              <input id="email" value={profile?.email ?? ""} disabled />
            </div>
          </div>

          <div className="form-row">
            <div className="field">
              <label htmlFor="phone">Phone</label>
              <input id="phone" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
            </div>
            <div className="field">
              <label htmlFor="dob">Date of Birth</label>
              <input
                id="dob"
                type="date"
                value={form.date_of_birth}
                onChange={(e) => setForm({ ...form, date_of_birth: e.target.value })}
              />
            </div>
          </div>

          <div className="field">
            <label htmlFor="address">Address</label>
            <input
              id="address"
              value={form.address}
              onChange={(e) => setForm({ ...form, address: e.target.value })}
            />
          </div>

          <div className="form-row">
            <div className="field">
              <label htmlFor="employment">Employment</label>
              <input
                id="employment"
                value={form.employment}
                onChange={(e) => setForm({ ...form, employment: e.target.value })}
              />
            </div>
            <div className="field">
              <label htmlFor="existing_loans">Existing Loans (count)</label>
              <input
                id="existing_loans"
                type="number"
                min={0}
                value={form.existing_loans}
                onChange={(e) => setForm({ ...form, existing_loans: e.target.value })}
              />
            </div>
          </div>

          <div className="form-row">
            <div className="field">
              <label htmlFor="monthly_income">Monthly Income</label>
              <input
                id="monthly_income"
                type="number"
                min={0}
                step="0.01"
                value={form.monthly_income}
                onChange={(e) => setForm({ ...form, monthly_income: e.target.value })}
              />
            </div>
            <div className="field">
              <label htmlFor="yearly_income">Yearly Income</label>
              <input
                id="yearly_income"
                type="number"
                min={0}
                step="0.01"
                value={form.yearly_income}
                onChange={(e) => setForm({ ...form, yearly_income: e.target.value })}
              />
            </div>
          </div>

          <div className="form-row">
            <div className="field">
              <label htmlFor="bank_account_number">Bank Account Number</label>
              <input
                id="bank_account_number"
                value={form.bank_account_number}
                onChange={(e) => setForm({ ...form, bank_account_number: e.target.value })}
              />
            </div>
            <div className="field">
              <label htmlFor="credit_score">Credit Score</label>
              <input
                id="credit_score"
                type="number"
                min={300}
                max={900}
                value={form.credit_score}
                onChange={(e) => setForm({ ...form, credit_score: e.target.value })}
              />
              <span className="field-hint">Manually entered; no credit bureau integration.</span>
            </div>
          </div>

          <div className="form-actions">
            <button type="submit" className="btn" disabled={saving}>
              {saving ? "Saving..." : "Save Changes"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
