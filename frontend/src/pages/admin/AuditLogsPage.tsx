import { useEffect, useState } from "react";
import * as adminService from "../../services/admin";
import { formatDateTime } from "../../utils/format";
import type { AuditLog } from "../../types";

export function AuditLogsPage() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    adminService.listAuditLogs().then(setLogs).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="empty-state">Loading audit logs...</div>;

  return (
    <div>
      <div className="page-header">
        <h1>Audit Logs</h1>
        <p>Traceable record of logins and business-critical changes.</p>
      </div>

      <div className="panel">
        {logs.length === 0 ? (
          <div className="empty-state">No audit log entries yet.</div>
        ) : (
          <div className="table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Action</th>
                  <th>Entity</th>
                  <th>Old Value</th>
                  <th>New Value</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log) => (
                  <tr key={log.id}>
                    <td>{formatDateTime(log.created_at)}</td>
                    <td>{log.action.replace(/_/g, " ")}</td>
                    <td>
                      {log.entity_type}
                      {log.entity_id ? ` #${log.entity_id}` : ""}
                    </td>
                    <td>{log.old_value ?? "-"}</td>
                    <td>{log.new_value ?? "-"}</td>
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
