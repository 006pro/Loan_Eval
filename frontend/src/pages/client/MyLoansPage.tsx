import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import * as loansService from "../../services/loans";
import { StatusBadge } from "../../components/StatusBadge";
import { formatCurrency } from "../../utils/format";
import type { Loan } from "../../types";

export function MyLoansPage() {
  const [loans, setLoans] = useState<Loan[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loansService.listMyLoans().then(setLoans).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="empty-state">Loading loans...</div>;

  return (
    <div>
      <div className="page-header">
        <h1>My Loans</h1>
        <p>Approved loans, including those awaiting the approval fee payment.</p>
      </div>

      <div className="panel">
        {loans.length === 0 ? (
          <div className="empty-state">You do not have any loans yet.</div>
        ) : (
          <div className="table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Loan Type</th>
                  <th>Approved Amount</th>
                  <th>Interest Rate</th>
                  <th>EMI</th>
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
                    <td>{formatCurrency(loan.emi_amount)}</td>
                    <td>{formatCurrency(loan.outstanding_principal)}</td>
                    <td>
                      <StatusBadge status={loan.status} />
                    </td>
                    <td>
                      <Link to={`/loans/${loan.id}`}>View</Link>
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
