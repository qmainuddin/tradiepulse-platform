"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useAuthStore } from "../../store/useAuthStore";
import { Wrench, Shield, Lock, Mail } from "lucide-react";

export default function LoginPage() {
  const { setAuth } = useAuthStore();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) return;

    // Simulate login & role assignment
    const role = email.includes("admin") ? "admin" : email.includes("tradie") ? "tradesperson" : "customer";

    setAuth({
      token: "mock-jwt-token-access",
      userId: "user-uuid-9999",
      email: email,
      role: role as any,
      firstName: email.split("@")[0],
      lastName: "User",
      isImpersonating: false,
    });

    if (role === "admin") {
      window.location.href = "/admin";
    } else if (role === "tradesperson") {
      window.location.href = "/tradie";
    } else {
      window.location.href = "/customer";
    }
  };

  return (
    <div className="max-w-md mx-auto py-12 space-y-6">
      <div className="text-center space-y-2">
        <div className="bg-sky-600 p-3 rounded-2xl text-white w-fit mx-auto shadow-md">
          <Wrench className="h-6 w-6" />
        </div>
        <h1 className="text-2xl font-black text-slate-900">Sign in to TradiePulse</h1>
        <p className="text-xs text-slate-500">Access your customer requests, tradie profile, or admin console</p>
      </div>

      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-4">
        {error && (
          <div className="bg-red-50 text-red-700 text-xs p-3 rounded-xl border border-red-200">
            {error}
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Email Address</label>
            <div className="relative">
              <Mail className="h-4 w-4 text-slate-400 absolute left-3 top-3" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.co.nz"
                className="w-full bg-slate-50 border border-slate-200 rounded-xl pl-9 pr-4 py-2 text-sm focus:ring-2 focus:ring-sky-500 focus:outline-none"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Password</label>
            <div className="relative">
              <Lock className="h-4 w-4 text-slate-400 absolute left-3 top-3" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-slate-50 border border-slate-200 rounded-xl pl-9 pr-4 py-2 text-sm focus:ring-2 focus:ring-sky-500 focus:outline-none"
              />
            </div>
          </div>

          <button
            type="submit"
            className="w-full bg-sky-600 hover:bg-sky-700 text-white font-bold py-2.5 rounded-xl text-xs transition shadow-sm"
          >
            Sign In with Email
          </button>
        </form>

        <div className="relative my-4">
          <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-slate-200" /></div>
          <div className="relative flex justify-center text-xs uppercase"><span className="bg-white px-2 text-slate-400">Or continue with</span></div>
        </div>

        <button
          type="button"
          onClick={() => {
            setEmail("google.user@gmail.com");
            setPassword("password123");
          }}
          className="w-full bg-slate-50 hover:bg-slate-100 border border-slate-200 text-slate-700 font-semibold py-2 rounded-xl text-xs transition flex items-center justify-center space-x-2"
        >
          <span>Google OAuth2 / OIDC</span>
        </button>

        <div className="text-center pt-2">
          <Link href="/signup" className="text-xs font-semibold text-sky-600 hover:underline">
            Don't have an account? Sign up (48h email activation)
          </Link>
        </div>
      </div>
    </div>
  );
}
