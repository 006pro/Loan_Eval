import { api } from "./api";
import type {
  AdminLoanApplication,
  AdminUser,
  ApplicationStatus,
  ApprovalFeeRule,
  ApprovalRequest,
  AuditLog,
  DurationRule,
  Loan,
  LoanType,
  PenaltyRule,
  RejectionRequest,
  RepaymentFrequency,
  RepaymentScheduleRow,
} from "../types";

export function listApplications(status?: ApplicationStatus): Promise<AdminLoanApplication[]> {
  const query = status ? `?status=${status}` : "";
  return api.get<AdminLoanApplication[]>(`/admin/loan-applications${query}`);
}

export function getApplication(id: number): Promise<AdminLoanApplication> {
  return api.get<AdminLoanApplication>(`/admin/loan-applications/${id}`);
}

export function approveApplication(id: number, payload: ApprovalRequest): Promise<Loan> {
  return api.post<Loan>(`/admin/loan-applications/${id}/approve`, payload);
}

export function rejectApplication(id: number, payload: RejectionRequest): Promise<AdminLoanApplication> {
  return api.post<AdminLoanApplication>(`/admin/loan-applications/${id}/reject`, payload);
}

export function getDurationRule(): Promise<DurationRule> {
  return api.get<DurationRule>("/admin/master/duration");
}

export function updateDurationRule(payload: DurationRule): Promise<DurationRule> {
  return api.put<DurationRule>("/admin/master/duration", payload);
}

export function getFeeRule(): Promise<ApprovalFeeRule> {
  return api.get<ApprovalFeeRule>("/admin/master/fees");
}

export function updateFeeRule(payload: ApprovalFeeRule): Promise<ApprovalFeeRule> {
  return api.put<ApprovalFeeRule>("/admin/master/fees", payload);
}

export function listLoanTypes(): Promise<LoanType[]> {
  return api.get<LoanType[]>("/admin/master/loan-types");
}

export interface LoanTypeInput {
  name: string;
  description?: string;
  interest_rate: string;
  min_amount: string;
  max_amount: string;
}

export function createLoanType(payload: LoanTypeInput): Promise<LoanType> {
  return api.post<LoanType>("/admin/master/loan-types", payload);
}

export function updateLoanType(id: number, payload: Partial<LoanTypeInput & { is_active: boolean }>): Promise<LoanType> {
  return api.put<LoanType>(`/admin/master/loan-types/${id}`, payload);
}

export function listRepaymentFrequencies(): Promise<RepaymentFrequency[]> {
  return api.get<RepaymentFrequency[]>("/admin/master/repayment-frequencies");
}

export function updateRepaymentFrequency(id: number, isActive: boolean): Promise<RepaymentFrequency> {
  return api.put<RepaymentFrequency>(`/admin/master/repayment-frequencies/${id}`, { is_active: isActive });
}

export function listPenaltyRules(): Promise<PenaltyRule[]> {
  return api.get<PenaltyRule[]>("/admin/master/penalties");
}

export function updatePenaltyRule(id: number, penaltyRate: string, isActive?: boolean): Promise<PenaltyRule> {
  return api.put<PenaltyRule>(`/admin/master/penalties/${id}`, {
    penalty_rate: penaltyRate,
    is_active: isActive,
  });
}

export function listLoans(status?: string): Promise<Loan[]> {
  const query = status ? `?status=${status}` : "";
  return api.get<Loan[]>(`/admin/loans${query}`);
}

export function getLoan(id: number): Promise<Loan> {
  return api.get<Loan>(`/admin/loans/${id}`);
}

export function getLoanSchedule(id: number): Promise<RepaymentScheduleRow[]> {
  return api.get<RepaymentScheduleRow[]>(`/admin/loans/${id}/schedule`);
}

export function listAuditLogs(limit = 200): Promise<AuditLog[]> {
  return api.get<AuditLog[]>(`/admin/audit-logs?limit=${limit}`);
}

export function listAdmins(): Promise<AdminUser[]> {
  return api.get<AdminUser[]>("/admin/admins");
}

export interface AdminCreateInput {
  email: string;
  password: string;
  name: string;
  employee_id: string;
}

export function createAdmin(payload: AdminCreateInput): Promise<AdminUser> {
  return api.post<AdminUser>("/admin/admins", payload);
}
