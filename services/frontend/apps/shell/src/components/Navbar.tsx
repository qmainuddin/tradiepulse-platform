"use client";

import React from "react";
import Link from "next/link";
import { useAuthStore } from "../store/useAuthStore";
import { Wrench, User, MessageSquare, Shield, LogOut, CheckCircle } from "lucide-react";

export const Navbar: React.FC = () => {
  const { token, role, firstName, clearAuth } = useAuthStore();

  return (
    <nav className="bg-white border-b border-slate-200 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <Link href="/" className="flex items-center space-x-2">
            <div className="bg-sky-600 p-2 rounded-lg text-white">
              <Wrench className="h-5 w-5" />
            </div>
            <span className="text-xl font-black text-slate-900 tracking-tight">
              Tradie<span className="text-sky-600">Pulse</span>
            </span>
          </Link>

          <div className="flex items-center space-x-4">
            <Link
              href="/chat"
              className="text-sm font-semibold text-slate-700 hover:text-sky-600 flex items-center space-x-1"
            >
              <MessageSquare className="h-4 w-4" />
              <span>AI Booking</span>
            </Link>

            {role === "customer" && (
              <Link href="/customer" className="text-sm font-semibold text-slate-700 hover:text-sky-600">
                My Jobs
              </Link>
            )}

            {role === "tradesperson" && (
              <Link href="/tradie" className="text-sm font-semibold text-slate-700 hover:text-sky-600 flex items-center space-x-1">
                <CheckCircle className="h-4 w-4 text-emerald-600" />
                <span>Tradie Portal</span>
              </Link>
            )}

            {(role === "admin" || role === "super_admin") && (
              <Link href="/admin" className="text-sm font-semibold text-slate-700 hover:text-sky-600 flex items-center space-x-1">
                <Shield className="h-4 w-4 text-sky-600" />
                <span>Admin Console</span>
              </Link>
            )}

            {token ? (
              <div className="flex items-center space-x-3 pl-4 border-l border-slate-200">
                <span className="text-xs font-semibold text-slate-600">
                  Kia ora, {firstName}
                </span>
                <button
                  onClick={() => clearAuth()}
                  className="p-1.5 text-slate-400 hover:text-red-600 rounded-md hover:bg-slate-100"
                  title="Logout"
                >
                  <LogOut className="h-4 w-4" />
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <Link
                  href="/login"
                  className="text-sm font-semibold text-slate-700 hover:text-sky-600 px-3 py-1.5"
                >
                  Log in
                </Link>
                <Link
                  href="/signup"
                  className="bg-sky-600 hover:bg-sky-700 text-white text-sm font-semibold px-4 py-2 rounded-lg transition shadow-sm"
                >
                  Get Started
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};
