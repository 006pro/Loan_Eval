import { api } from "./api";
import type { LoanType } from "../types";

export function listActiveLoanTypes(): Promise<LoanType[]> {
  return api.get<LoanType[]>("/loan-types");
}

export function getLoanType(id: number): Promise<LoanType> {
  return api.get<LoanType>(`/loan-types/${id}`);
}
