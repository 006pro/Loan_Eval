import { useState } from "react";
import type { FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import { ApiError } from "../../services/api";

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await login(email, password);
      navigate("/dashboard");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Unable to log in");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="auth-page">
      <div>
        <div className="auth-brand">
          Loan Management System
          <small>Client Portal</small>
        </div>
        <div className="auth-card">
          <h1>Log In</h1>
          {error && <div className="alert alert-error">{error}</div>}
          <form onSubmit={handleSubmit} noValidate>
            <div className="field">
              <label htmlFor="email">Email</label>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="email"
              />
            </div>
            <div className="field">
              <label htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
              />
            </div>
            <button type="submit" className="btn" disabled={submitting} style={{ width: "100%" }}>
              {submitting ? "Logging in..." : "Log In"}
            </button>
          </form>
          <p className="auth-footer">
            New client? <Link to="/register">Create an account</Link>
          </p>
          <p className="auth-footer">
            <Link to="/admin/login">Administrator login</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
