import React from "react";
import { ChatInterface } from "../../components/ChatInterface";

export default function ChatPage() {
  return (
    <div className="py-6 space-y-6">
      <div className="text-center max-w-xl mx-auto space-y-2">
        <h1 className="text-2xl sm:text-3xl font-black text-slate-900">AI Problem Assessment & Dispatch</h1>
        <p className="text-sm text-slate-600">
          Chat with our agent to specify your problem. We'll identify the required trade and match the highest-rated available specialist in Christchurch.
        </p>
      </div>
      <ChatInterface />
    </div>
  );
}
