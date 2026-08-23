import React from "react";
import { CheckCircle2, PlayCircle } from "lucide-react";
import Logo from "../components/Logo";
import { Panel } from "../components/Panel";
import { PrimaryButton, GhostButton } from "../components/Buttons";
import RadialScore from "../components/RadialScore";

export default function Landing({ goApp }) {
  return (
    <div className="min-h-screen text-slate-100" style={{ background: "#05060c" }}>
      <div className="flex items-center justify-between px-10 py-5 border-b border-slate-900">
        <Logo />
        <div className="hidden md:flex items-center gap-8 text-sm text-slate-400">
          <span>Product</span><span>How It Works</span><span>Technology</span><span>Pricing</span>
        </div>
        <div className="flex items-center gap-4">
          <button onClick={() => goApp("dashboard")} className="text-sm text-slate-400">Dashboard</button>
          <PrimaryButton onClick={() => goApp("dashboard")}>Connect Wallet</PrimaryButton>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-10 py-20 grid md:grid-cols-2 gap-14 items-center">
        <div>
          <span className="inline-block text-xs font-semibold px-3 py-1 rounded-full mb-6"
            style={{ background: "rgba(168,85,247,0.15)", color: "#c4b5fd" }}>
            AI-POWERED MEDIA VERIFICATION
          </span>
          <h1 className="text-5xl font-bold leading-tight mb-6">
            Detect Deepfakes.<br />Verify Authenticity.<br />
            <span style={{ background: "linear-gradient(90deg,#a855f7,#3b82f6)", WebkitBackgroundClip: "text", color: "transparent" }}>
              Trust the Truth.
            </span>
          </h1>
          <p className="text-slate-400 mb-8 max-w-md">
            Advanced AI detects manipulated media. Blockchain ensures tamper-proof verification.
          </p>
          <div className="flex gap-4">
            <PrimaryButton onClick={() => goApp("upload")}>Verify a Video</PrimaryButton>
            <GhostButton><PlayCircle size={16} /> Watch Demo</GhostButton>
          </div>
          <div className="grid grid-cols-2 gap-6 mt-14 text-sm">
            {[
              ["AI Deepfake Detection", "State-of-the-art AI models"],
              ["SHA-256 Integrity", "Cryptographic fingerprinting"],
              ["Blockchain Verified", "Tamper-proof on-chain records"],
              ["Polygon Network", "Secure · Scalable · Low Cost"],
            ].map(([t, s]) => (
              <div key={t}>
                <p className="font-semibold text-slate-200">{t}</p>
                <p className="text-slate-500 text-xs">{s}</p>
              </div>
            ))}
          </div>
        </div>

        <Panel className="p-8 flex flex-col items-center justify-center">
          <RadialScore value={93} color="#22d3ee" label="CONFIDENCE" sub="SCORE" />
          <div className="mt-6 flex items-center gap-2 text-emerald-400 text-sm font-semibold">
            <CheckCircle2 size={16} /> VERIFIED
          </div>
        </Panel>
      </div>
    </div>
  );
}
