"use client";

import React, { useState } from "react";
import { Star, Clock, CheckCircle2, AlertCircle, Wrench } from "lucide-react";

export default function CustomerDashboard() {
  const [activeTab, setActiveTab] = useState<"ongoing" | "pending" | "completed" | "cancelled">("ongoing");
  const [ratingModalJobId, setRatingModalJobId] = useState<string | null>(null);
  const [score, setScore] = useState(5);
  const [review, setReview] = useState("");

  const mockJobs = [
    {
      id: "job-101",
      title: "Kitchen Mixer Tap Replacement",
      trade: "plumber",
      tradieName: "Dave Riccarton Plumbing",
      status: "in_progress",
      address: "42 Straven Rd, Riccarton, Christchurch",
      cost: 145.00,
      createdAt: "Today at 9:30 AM",
    },
    {
      id: "job-102",
      title: "Switchboard RCD Tripping",
      trade: "electrician",
      tradieName: "Liam Smith Electrical",
      status: "completed",
      address: "15 Papanui Rd, Merivale, Christchurch",
      cost: 210.00,
      createdAt: "Yesterday",
      hasRated: false,
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-200 pb-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900">Customer Job Dashboard</h1>
          <p className="text-sm text-slate-500">Track and manage your household repair requests</p>
        </div>
        <div className="flex space-x-2 bg-slate-200/60 p-1 rounded-xl text-xs font-semibold">
          {(["ongoing", "pending", "completed", "cancelled"] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-3 py-1.5 rounded-lg capitalize transition ${
                activeTab === tab ? "bg-white text-slate-900 shadow-sm" : "text-slate-600 hover:text-slate-900"
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      {/* Jobs List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {mockJobs.map((job) => (
          <div key={job.id} className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm space-y-4">
            <div className="flex justify-between items-start">
              <div>
                <span className="text-[10px] uppercase font-bold tracking-wider text-sky-600 bg-sky-50 px-2 py-0.5 rounded">
                  {job.trade}
                </span>
                <h3 className="font-bold text-slate-900 text-base mt-1">{job.title}</h3>
                <p className="text-xs text-slate-500">{job.address}</p>
              </div>
              <span className={`text-xs font-semibold px-2.5 py-1 rounded-full ${
                job.status === "in_progress" ? "bg-amber-100 text-amber-800" : "bg-emerald-100 text-emerald-800"
              }`}>
                {job.status === "in_progress" ? "In Progress" : "Completed"}
              </span>
            </div>

            <div className="pt-2 border-t border-slate-100 flex justify-between items-center text-xs">
              <div>
                <p className="text-slate-400">Assigned Specialist</p>
                <p className="font-semibold text-slate-800">{job.tradieName}</p>
              </div>
              <div className="text-right">
                <p className="text-slate-400">Estimated Cost</p>
                <p className="font-bold text-slate-900">${job.cost} NZD</p>
              </div>
            </div>

            {job.status === "completed" && !job.hasRated && (
              <button
                onClick={() => setRatingModalJobId(job.id)}
                className="w-full bg-amber-500 hover:bg-amber-600 text-white font-semibold py-2 rounded-xl text-xs transition flex items-center justify-center space-x-1"
              >
                <Star className="h-4 w-4 fill-white" />
                <span>Rate & Review Tradesperson</span>
              </button>
            )}
          </div>
        ))}
      </div>

      {/* Rating Modal */}
      {ratingModalJobId && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl p-6 max-w-md w-full shadow-2xl space-y-4">
            <h3 className="text-lg font-bold text-slate-900">Rate your Tradesperson</h3>
            <p className="text-xs text-slate-500">Your feedback maintains quality and trust on the TradiePulse platform.</p>
            <div className="flex justify-center space-x-2 py-2">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  onClick={() => setScore(star)}
                  className="p-1 hover:scale-110 transition"
                >
                  <Star className={`h-8 w-8 ${star <= score ? "text-amber-400 fill-amber-400" : "text-slate-200"}`} />
                </button>
              ))}
            </div>
            <textarea
              rows={3}
              value={review}
              onChange={(e) => setReview(e.target.value)}
              placeholder="How was the punctuality, cleanliness, and quality of work?"
              className="w-full bg-slate-50 border border-slate-200 rounded-xl p-3 text-sm focus:ring-2 focus:ring-sky-500 focus:outline-none"
            />
            <div className="flex justify-end space-x-2">
              <button
                onClick={() => setRatingModalJobId(null)}
                className="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-lg"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  alert("Thank you! Rating submitted successfully.");
                  setRatingModalJobId(null);
                }}
                className="px-4 py-2 text-xs font-semibold bg-sky-600 hover:bg-sky-700 text-white rounded-lg"
              >
                Submit Review
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
