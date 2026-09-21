import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import * as adminService from "../../services/admin";
import { StatusBadge } from "../../components/StatusBadge";
import { formatCurrency } from "../../utils/format";
import type { Loan, LoanStatus } from "../../types";

const STATUS_FILTERS: { label: string; value: LoanStatus | "ALL" }[] = [
  { label: "All", value: "ALL" },
  { label: "Pending Fee", value: "PENDING_FEE" },
  { label: "Active", value: "ACTIVE" },
  { label: "Overdue", value: "OVERDUE" },
  { label: "Completed", value: "COMPLETED" },
];

export function LoansPage() {
  const [loans, setLoans] = useState<Loan[]>([]);
  const [statusFilter, setStatusFilter] = useState<LoanStatus | "ALL">("ALL");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    adminService
      .listLoans(statusFilter === "ALL" ? undefined : statusFilter)
      .then(setLoans)
      .finally(() => setLoading(false));
  }, [statusFilter]);

  return (
    <div>
      <div className="page-header">
        <h1>Loans</h1>
        <p>All loans created from approved applications.</p>
      </div>

      <div className="panel">
        <div className="panel-header">
          <h2>Loans</h2>
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value as LoanStatus | "ALL")}>
            {STATUS_FILTERS.map((filter) => (
              <option key={filter.value} value={filter.value}>
                {filter.label}
              </option>
            ))}
          </select>
        </div>

        {loading ? (
          <div className="empty-state">Loading loans...</div>
        ) : loans.length === 0 ? (
          <div className="empty-state">No loans match this filter.</div>
        ) : (
          <div className="table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Loan Type</th>
                  <th>Approved Amount</th>
                  <th>Interest Rate</th>
                  <th>Outstanding Principal</th>
                  <th>Status</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {loans.map((loan) => (
                  <tr key={loan.id}>
                    <td>{loan.loan_type_name}</td>
                    <td>{formatCurrency(loan.approved_amount)}</td>
                    <td>{loan.interest_rate}%</td>
                    <td>{formatCurrency(loan.outstanding_principal)}</td>
                    <td>
                      <StatusBadge status={loan.status} />
                    </td>
                    <td>
                      <Link to={`/admin/loans/${loan.id}`}>View</Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
