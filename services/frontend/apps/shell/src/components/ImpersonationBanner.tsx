"use client";

import React from "react";
import { useAuthStore } from "../store/useAuthStore";
import { AlertTriangle, LogOut } from "lucide-react";

export const ImpersonationBanner: React.FC = () => {
  const { isImpersonating, firstName, lastName, email, clearAuth } = useAuthStore();

  if (!isImpersonating) return null;

  return (
    <div className="bg-amber-600 text-white px-4 py-2 flex items-center justify-between shadow-md sticky top-0 z-50 animate-pulse">
      <div className="flex items-center space-x-2 text-sm font-semibold">
        <AlertTriangle className="h-5 w-5 text-yellow-200" />
        <span>
          IMPERSONATION ACTIVE: You are currently acting as{" "}
          <span className="underline">{firstName} {lastName}</span> ({email}). All actions are audited.
        </span>
      </div>
      <button
        onClick={() => {
          clearAuth();
          window.location.href = "/admin";
        }}
        className="bg-amber-800 hover:bg-amber-900 text-xs px-3 py-1.5 rounded font-medium flex items-center space-x-1 transition"
      >
        <LogOut className="h-3.5 w-3.5" />
        <span>End Impersonation</span>
      </button>
    </div>
  );
};
