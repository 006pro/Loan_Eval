export type UserRole = "CLIENT" | "ADMIN";

export type ApplicationStatus = "SUBMITTED" | "UNDER_REVIEW" | "APPROVED" | "REJECTED";
export type LoanStatus = "PENDING_FEE" | "ACTIVE" | "OVERDUE" | "COMPLETED";
export type FeeStatus = "PENDING" | "PAID";
export type ScheduleStatus = "PENDING" | "PAID" | "OVERDUE";
export type RepaymentFrequencyCode = "MONTHLY" | "QUARTERLY" | "HALF_YEARLY" | "YEARLY";
export type CalculationFrequency = "DAILY" | "WEEKLY";
export type TransactionType =
  | "DEPOSIT"
  | "LOAN_DISBURSEMENT"
  | "APPROVAL_FEE_PAYMENT"
  | "EMI_PAYMENT"
  | "PRINCIPAL_PREPAYMENT";
export type PaymentType = "EMI";

export interface TokenResponse {
  access_token: string;
  token_type: string;
  role: UserRole;
}

export interface CurrentUser {
  id: number;
  email: string;
  role: UserRole;
  display_name: string;
}

export interface ClientProfile {
  id: number;
  email: string;
  name: string;
  phone: string | null;
  address: string | null;
  date_of_birth: string | null;
  employment: string | null;
  monthly_income: string | null;
  yearly_income: string | null;
  existing_loans: number;
  bank_account_number: string | null;
  credit_score: number | null;
  created_at: string;
  updated_at: string;
}

export interface ClientProfileUpdateInput {
  name?: string;
  phone?: string;
  address?: string;
  date_of_birth?: string;
  employment?: string;
  monthly_income?: string;
  yearly_income?: string;
  existing_loans?: number;
  bank_account_number?: string;
  credit_score?: number;
}

export interface LoanType {
  id: number;
  name: string;
  description: string | null;
  interest_rate: string;
  min_amount: string;
  max_amount: string;
  is_active: boolean;
}

export interface DurationRule {
  minimum_months: number;
  maximum_months: number;
}

export interface ApprovalFeeRule {
  minimum_fee_percent: string;
  maximum_fee_percent: string;
}

export interface RepaymentFrequency {
  id: number;
  code: RepaymentFrequencyCode;
  is_active: boolean;
}

export interface PenaltyRule {
  id: number;
  repayment_frequency: RepaymentFrequencyCode;
  calculation_frequency: CalculationFrequency;
  penalty_rate: string;
  is_active: boolean;
}

export interface ApplicationConfig {
  minimum_duration_months: number;
  maximum_duration_months: number;
  active_repayment_frequencies: RepaymentFrequencyCode[];
}

export interface LoanApplicationRequest {
  loan_type_id: number;
  requested_amount: string;
  requested_duration_months: number;
  requested_frequency: RepaymentFrequencyCode;
}

export interface LoanApplicationPreview {
  loan_type_id: number;
  loan_type_name: string;
  requested_amount: string;
  interest_rate: string;
  duration_months: number;
  repayment_frequency: RepaymentFrequencyCode;
  number_of_installments: number;
  estimated_installment_amount: string;
  estimated_total_interest: string;
  estimated_total_payable: string;
}

export interface LoanApplication {
  id: number;
  loan_type_id: number;
  loan_type_name: string;
  requested_amount: string;
  requested_duration_months: number;
  requested_frequency: RepaymentFrequencyCode;
  status: ApplicationStatus;
  rejection_reason: string | null;
  submitted_at: string;
  evaluated_at: string | null;
}

export interface AdminClientSummary {
  id: number;
  name: string;
  phone: string | null;
  monthly_income: string | null;
  yearly_income: string | null;
  existing_loans: number;
  credit_score: number | null;
}

export interface AdminLoanApplication {
  id: number;
  client: AdminClientSummary;
  loan_type_id: number;
  loan_type_name: string;
  interest_rate: string;
  requested_amount: string;
  requested_duration_months: number;
  requested_frequency: RepaymentFrequencyCode;
  status: ApplicationStatus;
  rejection_reason: string | null;
  submitted_at: string;
  evaluated_at: string | null;
}

export interface ApprovalRequest {
  approved_amount: string;
  approval_fee_percent: string;
  credit_score?: number;
  remarks?: string;
}

export interface RejectionRequest {
  rejection_reason: string;
  credit_score?: number;
  remarks?: string;
}

export interface LoanFee {
  id: number;
  fee_percentage: string;
  fee_amount: string;
  status: FeeStatus;
  calculated_at: string;
  paid_at: string | null;
}

export interface Loan {
  id: number;
  application_id: number;
  loan_type_id: number;
  loan_type_name: string;
  approved_amount: string;
  interest_rate: string;
  duration_months: number;
  repayment_frequency: RepaymentFrequencyCode;
  emi_amount: string;
  outstanding_principal: string;
  start_date: string | null;
  end_date: string | null;
  status: LoanStatus;
  fee: LoanFee | null;
}

export interface RepaymentScheduleRow {
  id: number;
  installment_number: number;
  due_date: string;
  opening_principal: string;
  scheduled_principal: string;
  scheduled_interest: string;
  scheduled_amount: string;
  paid_principal: string;
  paid_interest: string;
  paid_amount: string;
  remaining_principal: string;
  status: ScheduleStatus;
  paid_at: string | null;
}

export interface Payment {
  id: number;
  loan_id: number;
  schedule_id: number;
  payment_type: PaymentType;
  amount: string;
  principal_amount: string;
  interest_amount: string;
  penalty_amount: string;
  payment_date: string;
}

export interface PrepaymentResult {
  id: number;
  loan_id: number;
  amount: string;
  principal_reduction: string;
  created_at: string;
}

export interface VirtualAccount {
  id: number;
  account_number: string;
  balance: string;
  status: "ACTIVE" | "CLOSED";
  created_at: string;
}

export interface AccountTransaction {
  id: number;
  transaction_type: TransactionType;
  amount: string;
  balance_before: string;
  balance_after: string;
  reference_type: string | null;
  reference_id: number | null;
  created_at: string;
}

export interface AuditLog {
  id: number;
  user_id: number | null;
  action: string;
  entity_type: string;
  entity_id: number | null;
  old_value: string | null;
  new_value: string | null;
  created_at: string;
}
