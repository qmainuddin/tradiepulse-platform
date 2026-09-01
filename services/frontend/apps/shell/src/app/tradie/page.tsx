"use client";

import React, { useState } from "react";
import { ShieldCheck, Upload, FileText, CheckCircle2, AlertCircle, Clock, MapPin } from "lucide-react";

export default function TradiePortalPage() {
  const [currentStep, setCurrentStep] = useState(1);
  const [trade, setTrade] = useState("plumber");
  const [licenceNumber, setLicenceNumber] = useState("");
  const [irdNumber, setIrdNumber] = useState("");
  const [insurancePolicy, setInsurancePolicy] = useState("");
  const [radiusKm, setRadiusKm] = useState(25);
  const [isSubmitted, setIsSubmitted] = useState(false);

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl sm:text-3xl font-black text-slate-900">Tradesperson Compliance & Verification Portal</h1>
        <p className="text-sm text-slate-500">
          Complete New Zealand trade qualification, licensing, and IRD verification to start receiving matched jobs in Christchurch.
        </p>
      </div>

      {/* Verification Stepper */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
        <div className="flex justify-between items-center mb-8">
          {[
            { step: 1, title: "Trade & Scope" },
            { step: 2, title: "NZ Licence (EWRB/PGDB)" },
            { step: 3, title: "Tax & Insurance" },
            { step: 4, title: "Review & Dispatch Area" },
          ].map((s) => (
            <div key={s.step} className="flex items-center space-x-2">
              <div className={`h-8 w-8 rounded-full flex items-center justify-center text-xs font-bold ${
                currentStep >= s.step ? "bg-sky-600 text-white" : "bg-slate-100 text-slate-400"
              }`}>
                {s.step}
              </div>
              <span className={`text-xs font-semibold hidden md:inline ${
                currentStep >= s.step ? "text-slate-900" : "text-slate-400"
              }`}>
                {s.title}
              </span>
            </div>
          ))}
        </div>

        {isSubmitted ? (
          <div className="text-center py-8 space-y-4">
            <div className="bg-emerald-100 text-emerald-700 p-4 rounded-full w-16 h-16 mx-auto flex items-center justify-center">
              <CheckCircle2 className="h-8 w-8" />
            </div>
            <h3 className="text-xl font-bold text-slate-900">Verification Package Submitted!</h3>
            <p className="text-sm text-slate-600 max-w-md mx-auto">
              Your documentation has been queued for Admin verification review against the NZ PGDB/EWRB register and IRD checksum gates. You will receive an email confirmation once activated.
            </p>
          </div>
        ) : (
          <div className="space-y-6">
            {currentStep === 1 && (
              <div className="space-y-4">
                <h3 className="font-bold text-slate-900 text-base">Select your Primary Trade in New Zealand</h3>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  {[
                    { id: "plumber", name: "Plumber & Drainlayer", board: "PGDB Board" },
                    { id: "electrician", name: "Electrician", board: "EWRB Board" },
                    { id: "mechanic", name: "Automotive Mechanic", board: "NZQA Level 4 / MTA" },
                  ].map((t) => (
                    <button
                      key={t.id}
                      type="button"
                      onClick={() => setTrade(t.id)}
                      className={`p-4 rounded-xl border text-left transition ${
                        trade === t.id ? "border-sky-600 bg-sky-50/50 ring-2 ring-sky-500" : "border-slate-200 hover:border-slate-300"
                      }`}
                    >
                      <h4 className="font-bold text-sm text-slate-900">{t.name}</h4>
                      <p className="text-xs text-slate-500 mt-1">{t.board}</p>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {currentStep === 2 && (
              <div className="space-y-4">
                <h3 className="font-bold text-slate-900 text-base">NZ Regulatory Registration & Practising Licence</h3>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    {trade === "plumber" ? "PGDB Registration / Licence Number" : trade === "electrician" ? "EWRB Registration Number" : "Trade Certificate Number / NZQA ID"}
                  </label>
                  <input
                    type="text"
                    value={licenceNumber}
                    onChange={(e) => setLicenceNumber(e.target.value)}
                    placeholder="e.g. PGDB-12345 or EWRB-98765"
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-sky-500 focus:outline-none"
                  />
                </div>
                <div className="border-2 border-dashed border-slate-200 rounded-xl p-6 text-center space-y-2">
                  <Upload className="h-6 w-6 text-slate-400 mx-auto" />
                  <p className="text-xs font-semibold text-slate-700">Upload Photo of Practising Licence Card (Front & Back)</p>
                  <p className="text-[10px] text-slate-400">PDF, PNG, JPG up to 10MB</p>
                </div>
              </div>
            )}

            {currentStep === 3 && (
              <div className="space-y-4">
                <h3 className="font-bold text-slate-900 text-base">Inland Revenue (IRD) & Public Liability Insurance</h3>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">NZ IRD Number (Mod-11 Validated)</label>
                  <input
                    type="text"
                    value={irdNumber}
                    onChange={(e) => setIrdNumber(e.target.value)}
                    placeholder="e.g. 123-456-789"
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-sky-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Public Liability Insurance Policy ($2M+ Minimum)</label>
                  <input
                    type="text"
                    value={insurancePolicy}
                    onChange={(e) => setInsurancePolicy(e.target.value)}
                    placeholder="Policy number and insurer name"
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-sky-500 focus:outline-none"
                  />
                </div>
              </div>
            )}

            {currentStep === 4 && (
              <div className="space-y-4">
                <h3 className="font-bold text-slate-900 text-base">Dispatch Area & Service Radius</h3>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Service Radius from Christchurch Base: <span className="font-bold text-sky-600">{radiusKm} km</span>
                  </label>
                  <input
                    type="range"
                    min={5}
                    max={60}
                    value={radiusKm}
                    onChange={(e) => setRadiusKm(Number(e.target.value))}
                    className="w-full"
                  />
                  <div className="flex justify-between text-[10px] text-slate-400 mt-1">
                    <span>Central (5km)</span>
                    <span>Greater Christchurch (25km)</span>
                    <span>Canterbury Region (60km)</span>
                  </div>
                </div>
              </div>
            )}

            <div className="flex justify-between pt-4 border-t border-slate-100">
              {currentStep > 1 ? (
                <button
                  type="button"
                  onClick={() => setCurrentStep(currentStep - 1)}
                  className="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-xl"
                >
                  Back
                </button>
              ) : <div />}
              {currentStep < 4 ? (
                <button
                  type="button"
                  onClick={() => setCurrentStep(currentStep + 1)}
                  className="px-6 py-2 bg-sky-600 hover:bg-sky-700 text-white text-xs font-bold rounded-xl shadow-sm"
                >
                  Continue
                </button>
              ) : (
                <button
                  type="button"
                  onClick={() => setIsSubmitted(true)}
                  className="px-6 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-xl shadow-sm"
                >
                  Submit for NZ Audit & Approval
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
