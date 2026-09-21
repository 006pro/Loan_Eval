const POSITIVE = new Set(["APPROVED", "ACTIVE", "PAID", "COMPLETED"]);
const NEGATIVE = new Set(["REJECTED", "OVERDUE"]);
const WARNING = new Set(["PENDING_FEE", "PENDING", "UNDER_REVIEW"]);

export function StatusBadge({ status }: { status: string }) {
  let className = "badge";
  if (POSITIVE.has(status)) className += " badge-success";
  else if (NEGATIVE.has(status)) className += " badge-danger";
  else if (WARNING.has(status)) className += " badge-warning";
  else className += " badge-info";

  return <span className={className}>{status.replace(/_/g, " ")}</span>;
}
