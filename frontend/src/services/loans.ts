import { api } from "./api";
import type { Loan, LoanFee, Payment, PrepaymentResult, RepaymentScheduleRow } from "../types";

export function listMyLoans(): Promise<Loan[]> {
  return api.get<Loan[]>("/loans");
}

export function getLoan(id: number): Promise<Loan> {
  return api.get<Loan>(`/loans/${id}`);
}

export function getSchedule(id: number): Promise<RepaymentScheduleRow[]> {
  return api.get<RepaymentScheduleRow[]>(`/loans/${id}/schedule`);
}

export function getFee(id: number): Promise<LoanFee> {
  return api.get<LoanFee>(`/loans/${id}/fee`);
}

export function payFee(id: number): Promise<Loan> {
  return api.post<Loan>(`/loans/${id}/fee/pay`);
}

export function payInstallment(id: number): Promise<Payment> {
  return api.post<Payment>(`/loans/${id}/payment`);
}

export function listPayments(id: number): Promise<Payment[]> {
  return api.get<Payment[]>(`/loans/${id}/payments`);
}

export function makePrepayment(id: number, amount: string): Promise<PrepaymentResult> {
  return api.post<PrepaymentResult>(`/loans/${id}/prepayment`, { amount });
}
