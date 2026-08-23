import React, { useEffect, useState } from "react";
import { CheckCircle2, RefreshCw } from "lucide-react";
import { Panel, PanelHeader } from "../components/Panel";
import { PrimaryButton } from "../components/Buttons";

export default function BlockchainPage({ onNext }) {
  const [step, setStep] = useState(1);
  useEffect(() => {
    const id = setInterval(() => setStep((s) => (s < 4 ? s + 1 : s)), 700);
    return () => clearInterval(id);
  }, []);
  const steps = ["Preparing Data", "Generating Hash", "Submitting Tx", "Confirming", "Recording"];

  return (
    <div className="grid grid-cols-2 gap-6 p-6">
      <Panel>
        <PanelHeader step="04" title="Blockchain Verification" subtitle="Creating tamper-proof verification record" />
        <div className="p-6">
          <p className="text-xs font-semibold text-slate-300 mb-2">Verification Details</p>
          <div className="text-[11px] text-slate-500 bg-slate-900/60 rounded-xl p-3 mb-4 break-all border border-slate-800">
            0f7a2b3c56d0b4f78bb203a91b2df34fc1a7d8e6b4f0c2d1a9e3f7b8c6d0a1e2
          </div>
          <div className="flex justify-between text-xs mb-4">
            <div><p className="text-slate-500">Status</p><p className="text-blue-400">Submitting...</p></div>
            <div><p className="text-slate-500">Analysis ID</p><p className="text-slate-300">BCV-2026-08-23-142536</p></div>
          </div>
          <div className="flex justify-between text-xs mb-6">
            <div><p className="text-slate-500">Timestamp</p><p className="text-slate-300">Aug 23, 2026 04:12 PM UTC</p></div>
            <div><p className="text-slate-500">Network</p><p className="text-slate-300">Polygon Amoy Testnet</p></div>
          </div>
          <p className="text-xs font-semibold text-slate-300 mb-3">Transaction Progress</p>
          <div className="space-y-2">
            {steps.map((s, i) => (
              <div key={s} className="flex items-center gap-3 text-xs">
                {i < step ? <CheckCircle2 size={14} className="text-emerald-400" /> :
                  i === step ? <RefreshCw size={14} className="text-blue-400 animate-spin" /> :
                  <div className="w-3.5 h-3.5 rounded-full border border-slate-700" />}
                <span className={i <= step ? "text-slate-300" : "text-slate-600"}>{s}</span>
              </div>
            ))}
          </div>
          <div className="flex justify-end mt-6">
            <PrimaryButton onClick={onNext}>Continue</PrimaryButton>
          </div>
        </div>
      </Panel>
      <Panel className="p-6">
        <p className="text-xs font-semibold text-slate-300 mb-3">Transaction Preview</p>
        <div className="text-xs space-y-3 text-slate-400">
          <div className="flex justify-between"><span>Network Fee</span><span className="text-slate-200">0.0003 MATIC</span></div>
          <div className="flex justify-between"><span>Estimated Time</span><span className="text-slate-200">15 – 20 sec</span></div>
          <div className="flex justify-between"><span>Contract</span><span className="text-slate-200">VerifyRegistry.sol</span></div>
        </div>
      </Panel>
    </div>
  );
}
//blockchain verification page with transaction progress and details, with a button to continue