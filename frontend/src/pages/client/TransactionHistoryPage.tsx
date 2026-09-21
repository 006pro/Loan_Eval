import { useEffect, useState } from "react";
import * as accountsService from "../../services/accounts";
import { formatCurrency, formatDateTime } from "../../utils/format";
import type { AccountTransaction } from "../../types";

export function TransactionHistoryPage() {
  const [transactions, setTransactions] = useState<AccountTransaction[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    accountsService.listMyTransactions().then(setTransactions).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="empty-state">Loading transactions...</div>;

  return (
    <div>
      <div className="page-header">
        <h1>Transaction History</h1>
        <p>Every balance-changing event on your Virtual Account.</p>
      </div>

      <div className="panel">
        {transactions.length === 0 ? (
          <div className="empty-state">No transactions yet.</div>
        ) : (
          <div className="table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Type</th>
                  <th>Amount</th>
                  <th>Balance Before</th>
                  <th>Balance After</th>
                  <th>Reference</th>
                </tr>
              </thead>
              <tbody>
                {transactions.map((txn) => (
                  <tr key={txn.id}>
                    <td>{formatDateTime(txn.created_at)}</td>
                    <td>{txn.transaction_type.replace(/_/g, " ")}</td>
                    <td>{formatCurrency(txn.amount)}</td>
                    <td>{formatCurrency(txn.balance_before)}</td>
                    <td>{formatCurrency(txn.balance_after)}</td>
                    <td>
                      {txn.reference_type ? `${txn.reference_type} #${txn.reference_id}` : "-"}
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
