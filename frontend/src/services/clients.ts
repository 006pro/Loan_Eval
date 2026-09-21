import { api } from "./api";
import type { ClientProfile, ClientProfileUpdateInput } from "../types";

export function getMyProfile(): Promise<ClientProfile> {
  return api.get<ClientProfile>("/clients/me");
}

export function updateMyProfile(payload: ClientProfileUpdateInput): Promise<ClientProfile> {
  return api.put<ClientProfile>("/clients/me", payload);
}
