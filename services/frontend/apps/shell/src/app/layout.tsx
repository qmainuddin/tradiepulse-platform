import type { Metadata } from "next";
import "./globals.css";
import { Navbar } from "../components/Navbar";
import { ImpersonationBanner } from "../components/ImpersonationBanner";

export const metadata: Metadata = {
  title: "TradiePulse — Instant AI Trades Matching in Christchurch & NZ",
  description: "Describe your household problem in plain English. Get connected to qualified, verified local plumbers, electricians, and mechanics in Christchurch, New Zealand.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-slate-50 text-slate-900 flex flex-col min-h-screen">
        <ImpersonationBanner />
        <Navbar />
        <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8">
          {children}
        </main>
        <footer className="bg-white border-t border-slate-200 py-6 text-center text-xs text-slate-500">
          <p>© {new Date().getFullYear()} TradiePulse New Zealand. Operating under Christchurch & Canterbury Regional Regulations & NZ Privacy Act 2020.</p>
        </footer>
      </body>
    </html>
  );
}
