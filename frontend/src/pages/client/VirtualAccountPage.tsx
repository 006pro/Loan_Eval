import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import * as accountsService from "../../services/accounts";
import { StatusBadge } from "../../components/StatusBadge";
import { formatCurrency, formatDateTime } from "../../utils/format";
import type { AccountTransaction, VirtualAccount } from "../../types";

export function VirtualAccountPage() {
  const [account, setAccount] = useState<VirtualAccount | null>(null);
  const [transactions, setTransactions] = useState<AccountTransaction[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([accountsService.getMyAccount(), accountsService.listMyTransactions()])
      .then(([acct, txns]) => {
        setAccount(acct);
        setTransactions(txns);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="empty-state">Loading account...</div>;
  if (!account) return <div className="alert alert-error">Virtual account not found.</div>;

  return (
    <div>
      <div className="page-header">
        <h1>Virtual Account</h1>
        <p>Your internal account used for approval fee payments, EMI payments, and prepayments.</p>
      </div>

      <div className="panel">
        <div className="summary-row">
          <div className="summary-item">
            <div className="label">Account Number</div>
            <div className="value">{account.account_number}</div>
          </div>
          <div className="summary-item">
            <div className="label">Balance</div>
            <div className="value">{formatCurrency(account.balance)}</div>
          </div>
          <div className="summary-item">
            <div className="label">Status</div>
            <div className="value">
              <StatusBadge status={account.status} />
            </div>
          </div>
        </div>
      </div>

      <div className="panel">
        <div className="panel-header">
          <h2>Recent Transactions</h2>
          <Link to="/transactions">View full history</Link>
        </div>
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
                  <th>Balance After</th>
                </tr>
              </thead>
              <tbody>
                {transactions.slice(0, 8).map((txn) => (
                  <tr key={txn.id}>
                    <td>{formatDateTime(txn.created_at)}</td>
                    <td>{txn.transaction_type.replace(/_/g, " ")}</td>
                    <td>{formatCurrency(txn.amount)}</td>
                    <td>{formatCurrency(txn.balance_after)}</td>
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
