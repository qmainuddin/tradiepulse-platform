"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Wrench, CheckCircle2, ShieldCheck } from "lucide-react";

export default function SignupPage() {
  const [role, setRole] = useState<"customer" | "tradesperson">("customer");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [phone, setPhone] = useState("");
  const [isRegistered, setIsRegistered] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsRegistered(true);
  };

  return (
    <div className="max-w-md mx-auto py-12 space-y-6">
      <div className="text-center space-y-2">
        <div className="bg-sky-600 p-3 rounded-2xl text-white w-fit mx-auto shadow-md">
          <Wrench className="h-6 w-6" />
        </div>
        <h1 className="text-2xl font-black text-slate-900">Create your TradiePulse Account</h1>
        <p className="text-xs text-slate-500">Fast customer registration or verified NZ tradesperson signup</p>
      </div>

      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-4">
        {isRegistered ? (
          <div className="text-center py-6 space-y-4">
            <div className="bg-emerald-100 text-emerald-700 p-3 rounded-full w-12 h-12 mx-auto flex items-center justify-center">
              <CheckCircle2 className="h-6 w-6" />
            </div>
            <h3 className="text-lg font-bold text-slate-900">Verification Email Dispatched!</h3>
            <p className="text-xs text-slate-600">
              We have sent a single-use 48-hour activation link to <span className="font-bold">{email}</span>. Click the link in your inbox to activate your account and start using TradiePulse.
            </p>
            <div className="pt-2">
              <Link href="/login" className="text-xs font-bold text-sky-600 hover:underline">
                Back to Sign in
              </Link>
            </div>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-2 bg-slate-100 p-1 rounded-xl text-xs font-bold">
              <button
                type="button"
                onClick={() => setRole("customer")}
                className={`py-2 rounded-lg transition ${
                  role === "customer" ? "bg-white text-slate-900 shadow-sm" : "text-slate-500"
                }`}
              >
                Customer
              </button>
              <button
                type="button"
                onClick={() => setRole("tradesperson")}
                className={`py-2 rounded-lg transition ${
                  role === "tradesperson" ? "bg-white text-slate-900 shadow-sm" : "text-slate-500"
                }`}
              >
                Tradesperson
              </button>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">First Name</label>
                <input
                  type="text"
                  required
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-sm focus:ring-2 focus:ring-sky-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Last Name</label>
                <input
                  type="text"
                  required
                  value={lastName}
                  onChange={(e) => setLastName(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-sm focus:ring-2 focus:ring-sky-500 focus:outline-none"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Email Address</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.co.nz"
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2 text-sm focus:ring-2 focus:ring-sky-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Mobile (NZ)</label>
              <input
                type="tel"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="021 123 4567"
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2 text-sm focus:ring-2 focus:ring-sky-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Password (Min 8 chars)</label>
              <input
                type="password"
                required
                minLength={8}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2 text-sm focus:ring-2 focus:ring-sky-500 focus:outline-none"
              />
            </div>

            <button
              type="submit"
              className="w-full bg-sky-600 hover:bg-sky-700 text-white font-bold py-2.5 rounded-xl text-xs transition shadow-sm"
            >
              Create Account
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
