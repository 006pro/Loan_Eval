import { api } from "./api";
import type { AccountTransaction, VirtualAccount } from "../types";

export function getMyAccount(): Promise<VirtualAccount> {
  return api.get<VirtualAccount>("/accounts/me");
}

export function listMyTransactions(): Promise<AccountTransaction[]> {
  return api.get<AccountTransaction[]>("/accounts/me/transactions");
}
