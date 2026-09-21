import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import type { UserRole } from "../types";

export function ProtectedRoute({ role }: { role: UserRole }) {
  const { user, loading } = useAuth();

  if (loading) {
    return <div className="empty-state">Loading...</div>;
  }

  if (!user) {
    return <Navigate to={role === "ADMIN" ? "/admin/login" : "/login"} replace />;
  }

  if (user.role !== role) {
    return <Navigate to={user.role === "ADMIN" ? "/admin" : "/dashboard"} replace />;
  }

  return <Outlet />;
}
