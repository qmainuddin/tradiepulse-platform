"use client";

import React, { useState } from "react";
import { Shield, UserCheck, CheckCircle, AlertTriangle, Search, UserX, Eye } from "lucide-react";
import { useAuthStore } from "../../store/useAuthStore";

export default function AdminConsolePage() {
  const { setAuth } = useAuthStore();
  const [activeView, setActiveView] = useState<"requests" | "verification" | "impersonate">("requests");

  // Step-Up Impersonation State
  const [targetEmail, setTargetEmail] = useState("");
  const [impersonationStep, setImpersonationStep] = useState<"enter_user" | "challenge_questions" | "success">("enter_user");
  const [challengeQuestions, setChallengeQuestions] = useState<string[]>([]);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [reason, setReason] = useState("");
  const [impersonateLoading, setImpersonateLoading] = useState(false);

  const mockRequests = [
    {
      id: "req-1",
      customer: "Hemi Te Wake",
      problem: "Burst main pipe in kitchen",
      trade: "plumber",
      suburb: "Riccarton, Christchurch",
      recommendedTradie: "Dave Riccarton Plumbing",
      status: "unassigned",
    },
    {
      id: "req-2",
      customer: "Emily Watson",
      problem: "No power in garage circuit",
      trade: "electrician",
      suburb: "Papanui, Christchurch",
      recommendedTradie: "Liam Smith Electrical",
      status: "unassigned",
    },
  ];

  const handleFetchChallenge = (e: React.FormEvent) => {
    e.preventDefault();
    if (!targetEmail) return;

    // Simulate fetching target user's registered security questions
    setChallengeQuestions(["first_pet", "mothers_maiden"]);
    setImpersonationStep("challenge_questions");
  };

  const handleVerifyAndImpersonate = (e: React.FormEvent) => {
    e.preventDefault();
    setImpersonateLoading(true);

    setTimeout(() => {
      setImpersonateLoading(false);
      // Mint mock impersonation session in Zustand store
      setAuth({
        token: "mock-impersonation-jwt-token",
        userId: "target-user-uuid-1234",
        email: targetEmail,
        role: "customer",
        firstName: targetEmail.split("@")[0],
        lastName: "(Customer)",
        isImpersonating: true,
        originalAdminId: "admin-super-uuid",
      });
      setImpersonationStep("success");
    }, 600);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center border-b border-slate-200 pb-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900">Admin Operations & Security Console</h1>
          <p className="text-sm text-slate-500">Dispatch requests, verify NZ qualifications, and perform audited step-up support</p>
        </div>
        <div className="flex space-x-2 bg-slate-200/60 p-1 rounded-xl text-xs font-semibold">
          {[
            { id: "requests", label: "Request Queue" },
            { id: "verification", label: "Tradie Approvals" },
            { id: "impersonate", label: "Step-Up Impersonation" },
          ].map((v) => (
            <button
              key={v.id}
              onClick={() => setActiveView(v.id as any)}
              className={`px-3 py-1.5 rounded-lg transition ${
                activeView === v.id ? "bg-white text-slate-900 shadow-sm" : "text-slate-600 hover:text-slate-900"
              }`}
            >
              {v.label}
            </button>
          ))}
        </div>
      </div>

      {activeView === "requests" && (
        <div className="space-y-4">
          <h3 className="font-bold text-slate-900 text-base">Incoming AI Request Queue</h3>
          <div className="grid grid-cols-1 gap-3">
            {mockRequests.map((req) => (
              <div key={req.id} className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm flex items-center justify-between">
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="text-[10px] font-bold uppercase bg-sky-100 text-sky-700 px-2 py-0.5 rounded">
                      {req.trade}
                    </span>
                    <span className="font-semibold text-slate-900 text-sm">{req.customer}</span>
                    <span className="text-xs text-slate-400">• {req.suburb}</span>
                  </div>
                  <p className="text-xs text-slate-600 mt-1">{req.problem}</p>
                  <p className="text-[11px] text-emerald-700 font-semibold mt-1">
                    AI Spatial Recommendation: {req.recommendedTradie}
                  </p>
                </div>
                <button
                  onClick={() => alert(`Assigned ${req.recommendedTradie} to ${req.customer}! Status set to 'assigned'.`)}
                  className="bg-slate-900 hover:bg-sky-600 text-white text-xs font-semibold px-4 py-2 rounded-lg transition"
                >
                  Approve & Dispatch
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeView === "verification" && (
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-4">
          <h3 className="font-bold text-slate-900 text-base">Pending NZ Qualification & Licensing Audits</h3>
          <div className="border border-slate-200 rounded-xl p-4 space-y-3">
            <div className="flex justify-between items-start">
              <div>
                <h4 className="font-bold text-slate-900">Dave Miller (Dave Riccarton Plumbing)</h4>
                <p className="text-xs text-slate-500">Trade: Plumber & Drainlayer · Christchurch</p>
                <div className="flex items-center space-x-2 mt-2 text-xs">
                  <span className="bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded font-medium">PGDB: #12345 (Active)</span>
                  <span className="bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded font-medium">IRD: Valid Mod-11</span>
                  <span className="bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded font-medium">Insurance: $2M Policy</span>
                </div>
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => alert("Verification Approved! Tradie is now active and ranked in PostGIS spatial matches.")}
                  className="bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold px-3 py-1.5 rounded-lg transition"
                >
                  Approve Tradie
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeView === "impersonate" && (
        <div className="max-w-xl mx-auto bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-6">
          <div className="flex items-center space-x-3 text-amber-600">
            <AlertTriangle className="h-6 w-6" />
            <div>
              <h3 className="font-bold text-slate-900 text-base">Step-Up Security Impersonation</h3>
              <p className="text-xs text-slate-500">Answering user's security questions is required. All actions are logged to tamper-evident audit trail.</p>
            </div>
          </div>

          {impersonationStep === "enter_user" && (
            <form onSubmit={handleFetchChallenge} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Target Customer / Tradie Email</label>
                <input
                  type="email"
                  required
                  value={targetEmail}
                  onChange={(e) => setTargetEmail(e.target.value)}
                  placeholder="e.g. customer@example.co.nz"
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-sky-500 focus:outline-none"
                />
              </div>
              <button
                type="submit"
                className="w-full bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold py-2.5 rounded-xl transition shadow-sm"
              >
                Initiate Step-Up Challenge
              </button>
            </form>
          )}

          {impersonationStep === "challenge_questions" && (
            <form onSubmit={handleVerifyAndImpersonate} className="space-y-4">
              <div className="bg-amber-50 border border-amber-200 rounded-xl p-3 text-xs text-amber-800">
                Security Step-Up required for <span className="font-bold">{targetEmail}</span>
              </div>
              {challengeQuestions.map((q) => (
                <div key={q}>
                  <label className="block text-xs font-semibold text-slate-700 mb-1 capitalize">
                    {q.replace("_", " ")} Answer:
                  </label>
                  <input
                    type="password"
                    required
                    placeholder="Enter answer provided by user"
                    value={answers[q] || ""}
                    onChange={(e) => setAnswers({ ...answers, [q]: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2 text-sm focus:ring-2 focus:ring-amber-500 focus:outline-none"
                  />
                </div>
              ))}
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Mandatory Audit Reason</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Customer phoned requesting booking troubleshooting"
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2 text-sm focus:ring-2 focus:ring-amber-500 focus:outline-none"
                />
              </div>
              <button
                type="submit"
                disabled={impersonateLoading}
                className="w-full bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold py-2.5 rounded-xl transition shadow-sm"
              >
                {impersonateLoading ? "Verifying Hash & Minting Token..." : "Authenticate & Impersonate"}
              </button>
            </form>
          )}

          {impersonationStep === "success" && (
            <div className="text-center py-4 space-y-3">
              <div className="bg-emerald-100 text-emerald-700 p-3 rounded-full w-12 h-12 mx-auto flex items-center justify-center">
                <CheckCircle className="h-6 w-6" />
              </div>
              <h4 className="font-bold text-slate-900 text-sm">Impersonation Session Active!</h4>
              <p className="text-xs text-slate-500">
                You are now acting as {targetEmail}. Notice the prominent top warning banner.
              </p>
              <button
                onClick={() => window.location.href = "/customer"}
                className="bg-sky-600 hover:bg-sky-700 text-white text-xs font-bold px-4 py-2 rounded-lg"
              >
                Go to Customer Portal as User
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
