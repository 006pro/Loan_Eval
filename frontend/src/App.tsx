import { Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider, useAuth } from "./hooks/useAuth";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { ClientLayout } from "./layouts/ClientLayout";
import { AdminLayout } from "./layouts/AdminLayout";

import { LoginPage } from "./pages/client/LoginPage";
import { RegisterPage } from "./pages/client/RegisterPage";
import { DashboardPage } from "./pages/client/DashboardPage";
import { ProfilePage } from "./pages/client/ProfilePage";
import { LoanTypesPage } from "./pages/client/LoanTypesPage";
import { ApplyLoanPage } from "./pages/client/ApplyLoanPage";
import { MyApplicationsPage } from "./pages/client/MyApplicationsPage";
import { ApplicationDetailsPage } from "./pages/client/ApplicationDetailsPage";
import { MyLoansPage } from "./pages/client/MyLoansPage";
import { LoanDetailsPage } from "./pages/client/LoanDetailsPage";
import { VirtualAccountPage } from "./pages/client/VirtualAccountPage";
import { TransactionHistoryPage } from "./pages/client/TransactionHistoryPage";

import { AdminLoginPage } from "./pages/admin/AdminLoginPage";
import { AdminDashboardPage } from "./pages/admin/AdminDashboardPage";
import { LoanApplicationsPage } from "./pages/admin/LoanApplicationsPage";
import { ApplicationDetailsPage as AdminApplicationDetailsPage } from "./pages/admin/ApplicationDetailsPage";
import { LoansPage as AdminLoansPage } from "./pages/admin/LoansPage";
import { LoanDetailsPage as AdminLoanDetailsPage } from "./pages/admin/LoanDetailsPage";
import { MasterConfigPage } from "./pages/admin/MasterConfigPage";
import { AuditLogsPage } from "./pages/admin/AuditLogsPage";
import { AdminUsersPage } from "./pages/admin/AdminUsersPage";

function RootRedirect() {
  const { user, loading } = useAuth();
  if (loading) return <div className="empty-state">Loading...</div>;
  if (!user) return <Navigate to="/login" replace />;
  return <Navigate to={user.role === "ADMIN" ? "/admin" : "/dashboard"} replace />;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<RootRedirect />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/admin/login" element={<AdminLoginPage />} />

      <Route element={<ProtectedRoute role="CLIENT" />}>
        <Route element={<ClientLayout />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/loan-types" element={<LoanTypesPage />} />
          <Route path="/apply" element={<ApplyLoanPage />} />
          <Route path="/applications" element={<MyApplicationsPage />} />
          <Route path="/applications/:id" element={<ApplicationDetailsPage />} />
          <Route path="/loans" element={<MyLoansPage />} />
          <Route path="/loans/:id" element={<LoanDetailsPage />} />
          <Route path="/account" element={<VirtualAccountPage />} />
          <Route path="/transactions" element={<TransactionHistoryPage />} />
        </Route>
      </Route>

      <Route element={<ProtectedRoute role="ADMIN" />}>
        <Route element={<AdminLayout />}>
          <Route path="/admin" element={<AdminDashboardPage />} />
          <Route path="/admin/applications" element={<LoanApplicationsPage />} />
          <Route path="/admin/applications/:id" element={<AdminApplicationDetailsPage />} />
          <Route path="/admin/loans" element={<AdminLoansPage />} />
          <Route path="/admin/loans/:id" element={<AdminLoanDetailsPage />} />
          <Route path="/admin/master" element={<MasterConfigPage />} />
          <Route path="/admin/admins" element={<AdminUsersPage />} />
          <Route path="/admin/audit-logs" element={<AuditLogsPage />} />
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  );
}
