import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

const NAV_ITEMS = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/profile", label: "Profile" },
  { to: "/loan-types", label: "Loan Types" },
  { to: "/apply", label: "Apply for Loan" },
  { to: "/applications", label: "My Applications" },
  { to: "/loans", label: "My Loans" },
  { to: "/account", label: "Virtual Account" },
  { to: "/transactions", label: "Transactions" },
];

export function ClientLayout() {
  const { user, logout } = useAuth();

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-brand">
          Loan Management
          <small>Client Portal</small>
        </div>
        <ul className="sidebar-nav">
          {NAV_ITEMS.map((item) => (
            <li key={item.to}>
              <NavLink to={item.to} className={({ isActive }) => (isActive ? "active" : undefined)}>
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
