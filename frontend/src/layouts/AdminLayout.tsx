import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

const NAV_ITEMS = [
  { to: "/admin", label: "Dashboard", end: true },
  { to: "/admin/applications", label: "Loan Applications" },
  { to: "/admin/loans", label: "Loans" },
  { to: "/admin/master", label: "Master Configuration" },
  { to: "/admin/admins", label: "Admin Users" },
  { to: "/admin/audit-logs", label: "Audit Logs" },
];

export function AdminLayout() {
  const { user, logout } = useAuth();

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-brand">
          Loan Management
          <small>Admin Console</small>
        </div>
        <ul className="sidebar-nav">
          {NAV_ITEMS.map((item) => (
            <li key={item.to}>
              <NavLink
                to={item.to}
                end={item.end}
                className={({ isActive }) => (isActive ? "active" : undefined)}
              >
                {item.label}
              </NavLink>
            </li>
          ))}
        </ul>
        <div className="sidebar-footer">
          <div className="sidebar-user">
            <strong>{user?.display_name}</strong>
            {user?.email}
          </div>
          <button type="button" className="btn btn-secondary btn-small" onClick={logout}>
            Log Out
          </button>
        </div>
      </aside>
      <div className="main-area">
        <div className="topbar">
          <strong>{user?.display_name}</strong>
          <button type="button" className="btn btn-secondary btn-small" onClick={logout}>
            Log Out
          </button>
        </div>
        <main className="main-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
