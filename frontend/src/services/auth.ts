import { api } from "./api";
import type { CurrentUser, TokenResponse } from "../types";

export function login(email: string, password: string): Promise<TokenResponse> {
  return api.post<TokenResponse>("/auth/login", { email, password });
}

export function register(email: string, password: string, name: string, phone?: string): Promise<TokenResponse> {
  return api.post<TokenResponse>("/auth/register", { email, password, name, phone });
}

export function logout(): Promise<void> {
  return api.post<void>("/auth/logout");
}

export function getMe(): Promise<CurrentUser> {
  return api.get<CurrentUser>("/auth/me");
}
