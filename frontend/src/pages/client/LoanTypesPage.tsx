import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import * as loanTypesService from "../../services/loanTypes";
import { formatCurrency } from "../../utils/format";
import type { LoanType } from "../../types";

export function LoanTypesPage() {
  const [loanTypes, setLoanTypes] = useState<LoanType[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loanTypesService.listActiveLoanTypes().then(setLoanTypes).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="empty-state">Loading loan types...</div>;

  return (
    <div>
      <div className="page-header">
        <h1>Loan Types</h1>
        <p>Interest rates and amount limits are set by the bank and may change over time.</p>
      </div>

      <div className="panel">
        {loanTypes.length === 0 ? (
          <div className="empty-state">No loan types are currently available.</div>
        ) : (
          <div className="table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Description</th>
                  <th>Interest Rate</th>
                  <th>Minimum Amount</th>
                  <th>Maximum Amount</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {loanTypes.map((loanType) => (
                  <tr key={loanType.id}>
                    <td>{loanType.name}</td>
                    <td>{loanType.description ?? "-"}</td>
                    <td>{loanType.interest_rate}%</td>
                    <td>{formatCurrency(loanType.min_amount)}</td>
                    <td>{formatCurrency(loanType.max_amount)}</td>
                    <td>
                      <Link to={`/apply?loan_type_id=${loanType.id}`} className="btn btn-small">
                        Apply
                      </Link>
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
