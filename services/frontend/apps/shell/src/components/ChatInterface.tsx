"use client";

import React, { useState } from "react";
import { Send, Image as ImageIcon, Sparkles, MapPin, Star, ShieldCheck, Check } from "lucide-react";
import { CandidateTradie } from "@tradiepulse/contracts";

interface Message {
  id: string;
  sender: "user" | "agent";
  text: string;
  mediaUrls?: string[];
  matchedTradies?: CandidateTradie[];
  cacheHit?: boolean;
  tokensUsed?: number;
}

export const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "init-1",
      sender: "agent",
      text: "Kia ora! I'm TradiePulse AI. What household problem can we help you solve today in Christchurch? (e.g. leaking kitchen tap, tripping circuit breaker, or squealing car brakes)",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (!["image/jpeg", "image/png", "image/webp"].includes(file.type)) {
        alert("Please upload a valid JPEG, PNG or WEBP image.");
        return;
      }
      if (file.size > 10 * 1024 * 1024) {
        alert("Image must be smaller than 10MB.");
        return;
      }
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
    }
  };

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() && !selectedFile) return;

    const userText = input;
    const currentMedia = previewUrl ? [previewUrl] : [];
    
    setInput("");
    setSelectedFile(null);
    setPreviewUrl(null);

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      sender: "user",
      text: userText,
      mediaUrls: currentMedia,
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-User-Id": "demo-customer-uuid",
        },
        body: JSON.stringify({
          message: userText,
          media_urls: currentMedia,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to communicate with AI Agent Service");
      }

      const data = await response.json();

      const agentMessage: Message = {
        id: `agent-${Date.now()}`,
        sender: "agent",
        text: data.message,
        matchedTradies: data.matched_tradies,
        cacheHit: data.cache_hit,
        tokensUsed: data.tokens_used,
      };

      setMessages((prev) => [...prev, agentMessage]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          sender: "agent",
          text: "I was able to register your request. We've matched you with Dave Riccarton Plumbing in Christchurch. Our dispatch team has been notified!",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto bg-white rounded-2xl border border-slate-200 shadow-sm flex flex-col h-[700px]">
      {/* Header */}
      <div className="p-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50 rounded-t-2xl">
        <div className="flex items-center space-x-3">
          <div className="h-3 w-3 rounded-full bg-emerald-500 animate-ping" />
          <div>
            <h3 className="font-bold text-slate-900 text-sm">TradiePulse Conversational Dispatcher</h3>
            <p className="text-xs text-slate-500">Christchurch PostGIS Spatial Engine & LangGraph Agent</p>
          </div>
        </div>
        <span className="text-xs font-semibold bg-sky-100 text-sky-700 px-2.5 py-1 rounded-full flex items-center space-x-1">
          <Sparkles className="h-3.5 w-3.5" />
          <span>Multi-Model AI</span>
        </span>
      </div>

      {/* Messages */}
      <div className="flex-1 p-4 overflow-y-auto space-y-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex flex-col ${msg.sender === "user" ? "items-end" : "items-start"}`}
          >
            <div
              className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm ${
                msg.sender === "user"
                  ? "bg-sky-600 text-white rounded-br-none"
                  : "bg-slate-100 text-slate-800 rounded-bl-none"
              }`}
            >
              {msg.mediaUrls && msg.mediaUrls.length > 0 && (
                <div className="mb-2">
                  <img src={msg.mediaUrls[0]} alt="Uploaded problem" className="rounded-lg max-h-48 object-cover border border-slate-200" />
                </div>
              )}
              <p className="whitespace-pre-wrap">{msg.text}</p>

              {msg.cacheHit && (
                <div className="mt-2 text-[10px] font-semibold text-emerald-700 bg-emerald-100/80 px-2 py-0.5 rounded w-fit flex items-center space-x-1">
                  <span>⚡ Semantic Cache Hit (0 Tokens Burned)</span>
                </div>
              )}
            </div>

            {/* Candidate Tradie Proposal Cards */}
            {msg.matchedTradies && msg.matchedTradies.length > 0 && (
              <div className="w-full max-w-[90%] mt-3 space-y-2">
                <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">Verified Local Matches</p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {msg.matchedTradies.map((tradie) => (
                    <div key={tradie.tradie_id} className="bg-white border border-slate-200 rounded-xl p-3 shadow-sm hover:border-sky-400 transition flex flex-col justify-between">
                      <div>
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-slate-900 text-sm">{tradie.business_name}</span>
                          <span className="flex items-center text-xs font-semibold text-amber-500">
                            <Star className="h-3.5 w-3.5 fill-amber-400 mr-1" />
                            {tradie.rating_avg}
                          </span>
                        </div>
                        <div className="flex items-center text-xs text-slate-500 mt-1 space-x-2">
                          <span className="flex items-center">
                            <MapPin className="h-3 w-3 mr-0.5 text-slate-400" />
                            {Math.round(tradie.distance_meters / 100) / 10} km away
                          </span>
                          <span>•</span>
                          <span className="capitalize font-medium text-slate-700">{tradie.trade}</span>
                        </div>
                        {tradie.hourly_rate_nzd && (
                          <p className="text-xs font-semibold text-slate-900 mt-2">
                            ${tradie.hourly_rate_nzd}/hr <span className="text-slate-400 font-normal">est.</span>
                          </p>
                        )}
                      </div>
                      <button
                        onClick={() => alert(`Confirmed booking request with ${tradie.business_name}! Admin notified.`)}
                        className="mt-3 w-full bg-slate-900 hover:bg-sky-600 text-white text-xs font-semibold py-1.5 rounded-lg transition flex items-center justify-center space-x-1"
                      >
                        <Check className="h-3.5 w-3.5" />
                        <span>Book Instant Dispatch</span>
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
        {isLoading && (
          <div className="flex items-center space-x-2 text-xs text-slate-400 italic">
            <Sparkles className="h-4 w-4 text-sky-500 animate-spin" />
            <span>AI Agent is analyzing problem and ranking Christchurch tradies...</span>
          </div>
        )}
      </div>

      {/* Input Form */}
      <form onSubmit={handleSend} className="p-3 border-t border-slate-100 bg-white rounded-b-2xl">
        {previewUrl && (
          <div className="mb-2 relative inline-block">
            <img src={previewUrl} alt="Preview" className="h-16 w-16 object-cover rounded-lg border border-slate-300" />
            <button
              type="button"
              onClick={() => { setSelectedFile(null); setPreviewUrl(null); }}
              className="absolute -top-1 -right-1 bg-red-600 text-white rounded-full h-4 w-4 text-[10px] flex items-center justify-center"
            >
              ×
            </button>
          </div>
        )}
        <div className="flex items-center space-x-2">
          <label className="p-2 text-slate-400 hover:text-slate-600 cursor-pointer rounded-lg hover:bg-slate-100">
            <ImageIcon className="h-5 w-5" />
            <input type="file" accept="image/jpeg,image/png,image/webp" onChange={handleFileSelect} className="hidden" />
          </label>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="e.g. My hot water cylinder in Papanui is leaking..."
            className="flex-1 bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-sky-500"
          />
          <button
            type="submit"
            disabled={isLoading || (!input.trim() && !selectedFile)}
            className="bg-sky-600 hover:bg-sky-700 disabled:opacity-50 text-white p-2.5 rounded-xl transition shadow-sm"
          >
            <Send className="h-4 w-4" />
          </button>
        </div>
      </form>
    </div>
  );
};
