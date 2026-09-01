import { create } from "zustand";
import { UserRole } from "@tradiepulse/contracts";

interface AuthState {
  token: string | null;
  refreshToken: string | null;
  userId: string | null;
  email: string | null;
  role: UserRole | null;
  firstName: string | null;
  lastName: string | null;
  isImpersonating: boolean;
  originalAdminId: string | null;
  
  setAuth: (payload: {
    token: string;
    refreshToken?: string | null;
    userId: string;
    email: string;
    role: UserRole;
    firstName: string;
    lastName: string;
    isImpersonating?: boolean;
    originalAdminId?: string | null;
  }) => void;
  clearAuth: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: null,
  refreshToken: null,
  userId: null,
  email: null,
  role: null,
  firstName: null,
  lastName: null,
  isImpersonating: false,
  originalAdminId: null,

  setAuth: (payload) =>
    set({
      token: payload.token,
      refreshToken: payload.refreshToken ?? null,
      userId: payload.userId,
      email: payload.email,
      role: payload.role,
      firstName: payload.firstName,
      lastName: payload.lastName,
      isImpersonating: payload.isImpersonating ?? false,
      originalAdminId: payload.originalAdminId ?? null,
    }),

  clearAuth: () =>
    set({
      token: null,
      refreshToken: null,
      userId: null,
      email: null,
      role: null,
      firstName: null,
      lastName: null,
      isImpersonating: false,
      originalAdminId: null,
    }),
}));
