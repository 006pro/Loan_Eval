import { api } from "./api";
import type {
  ApplicationConfig,
  LoanApplication,
  LoanApplicationPreview,
  LoanApplicationRequest,
} from "../types";

export function getApplicationConfig(): Promise<ApplicationConfig> {
  return api.get<ApplicationConfig>("/loan-applications/config");
}

export function previewApplication(payload: LoanApplicationRequest): Promise<LoanApplicationPreview> {
  return api.post<LoanApplicationPreview>("/loan-applications/preview", payload);
}

export function submitApplication(payload: LoanApplicationRequest): Promise<LoanApplication> {
  return api.post<LoanApplication>("/loan-applications", payload);
}

export function listMyApplications(): Promise<LoanApplication[]> {
  return api.get<LoanApplication[]>("/loan-applications");
}

export function getApplication(id: number): Promise<LoanApplication> {
  return api.get<LoanApplication>(`/loan-applications/${id}`);
}
