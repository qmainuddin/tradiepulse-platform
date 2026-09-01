import React from "react";
import Link from "next/link";
import { Wrench, Zap, Car, ShieldCheck, MapPin, Sparkles, Clock, ArrowRight } from "lucide-react";

export default function HomePage() {
  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <section className="text-center py-12 px-4 max-w-4xl mx-auto space-y-6">
        <div className="inline-flex items-center space-x-2 bg-sky-50 border border-sky-200 text-sky-700 px-3 py-1 rounded-full text-xs font-semibold">
          <Sparkles className="h-4 w-4" />
          <span>Frugal & Resilient AI Marketplace · Christchurch & New Zealand</span>
        </div>
        <h1 className="text-4xl sm:text-5xl font-black text-slate-900 tracking-tight leading-tight">
          Describe your problem. <br />
          <span className="text-sky-600">Get matched with Christchurch’s top verified tradie in seconds.</span>
        </h1>
        <p className="text-lg text-slate-600 max-w-2xl mx-auto">
          No endless phone calls or forms. Chat naturally with our deterministic AI agent to pinpoint your plumbing, electrical, or mechanic needs, and receive ranked local quotes instantly.
        </p>
        <div className="flex flex-col sm:flex-row justify-center items-center gap-4 pt-4">
          <Link
            href="/chat"
            className="w-full sm:w-auto bg-sky-600 hover:bg-sky-700 text-white font-bold px-8 py-3.5 rounded-xl transition shadow-md hover:shadow-lg flex items-center justify-center space-x-2 text-base"
          >
            <span>Start AI Problem Assessment</span>
            <ArrowRight className="h-5 w-5" />
          </Link>
          <Link
            href="/tradie"
            className="w-full sm:w-auto bg-white border border-slate-300 hover:bg-slate-50 text-slate-700 font-semibold px-6 py-3.5 rounded-xl transition"
          >
            Join as a Verified Tradesperson
          </Link>
        </div>
      </section>

      {/* Trades Grid */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:border-sky-300 transition">
          <div className="bg-sky-100 text-sky-700 p-3 rounded-xl w-fit mb-4">
            <Wrench className="h-6 w-6" />
          </div>
          <h3 className="text-xl font-bold text-slate-900 mb-2">Plumbers & Drainlayers</h3>
          <p className="text-sm text-slate-600 mb-4">
            Leaking taps, burst pipes, blocked drains, hot water cylinder faults, PGDB licensed certifying plumbers.
          </p>
          <span className="text-xs font-semibold text-sky-600 bg-sky-50 px-2.5 py-1 rounded-md">
            Average arrival: 45 mins in Christchurch
          </span>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:border-amber-300 transition">
          <div className="bg-amber-100 text-amber-700 p-3 rounded-xl w-fit mb-4">
            <Zap className="h-6 w-6" />
          </div>
          <h3 className="text-xl font-bold text-slate-900 mb-2">Electricians & Inspectors</h3>
          <p className="text-sm text-slate-600 mb-4">
            Switchboard upgrades, tripping circuits, EV charger installation, rewiring, EWRB registered & audited.
          </p>
          <span className="text-xs font-semibold text-amber-600 bg-amber-50 px-2.5 py-1 rounded-md">
            100% Verified EWRB Practising Licences
          </span>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:border-emerald-300 transition">
          <div className="bg-emerald-100 text-emerald-700 p-3 rounded-xl w-fit mb-4">
            <Car className="h-6 w-6" />
          </div>
          <h3 className="text-xl font-bold text-slate-900 mb-2">Mobile Automotive Mechanics</h3>
          <p className="text-sm text-slate-600 mb-4">
            Engine diagnostics, brake repairs, battery replacements, pre-purchase inspections & WoF repairs.
          </p>
          <span className="text-xs font-semibold text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-md">
            On-site mobile dispatch in Canterbury
          </span>
        </div>
      </section>

      {/* Trust & Architecture Features */}
      <section className="bg-slate-900 text-white rounded-3xl p-8 sm:p-12 space-y-8">
        <div className="max-w-2xl">
          <h2 className="text-2xl sm:text-3xl font-black mb-3">Enterprise Resilience & Privacy Built-In</h2>
          <p className="text-slate-400 text-sm">
            TradiePulse is engineered to showcase state-of-the-art AI cost-control and strict safety gates.
          </p>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="space-y-2">
            <ShieldCheck className="h-6 w-6 text-sky-400" />
            <h4 className="font-bold text-sm">Multi-Stage NZ Verification</h4>
            <p className="text-xs text-slate-400">Pluggable EWRB, PGDB, IRD mod-11 checksums & photo ID checks.</p>
          </div>
          <div className="space-y-2">
            <MapPin className="h-6 w-6 text-sky-400" />
            <h4 className="font-bold text-sm">PostGIS Spatial Matching</h4>
            <p className="text-xs text-slate-400">Sub-millisecond nearest tradie ranking respecting radius and live availability.</p>
          </div>
          <div className="space-y-2">
            <Sparkles className="h-6 w-6 text-sky-400" />
            <h4 className="font-bold text-sm">Deterministic State Machine</h4>
            <p className="text-xs text-slate-400">LangGraph typed schema gates prevent hallucination and control flow drift.</p>
          </div>
          <div className="space-y-2">
            <Clock className="h-6 w-6 text-sky-400" />
            <h4 className="font-bold text-sm">Semantic & Prompt Caching</h4>
            <p className="text-xs text-slate-400">Redis semantic caching avoids duplicate LLM burn for standard inquiries.</p>
          </div>
        </div>
      </section>
    </div>
  );
}
