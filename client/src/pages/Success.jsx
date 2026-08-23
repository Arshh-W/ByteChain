import React from "react";
import { CheckCircle2, ExternalLink } from "lucide-react";
import { Panel, PanelHeader } from "../components/Panel";
import { PrimaryButton, GhostButton } from "../components/Buttons";

export default function SuccessPage({ onNext }) {
  return (
    <div className="p-6 flex items-center justify-center min-h-[70vh]">
      <Panel className="p-10 max-w-md w-full text-center">
        <PanelHeader step="05" title="Verification Success" />
        <div className="pt-8 pb-4 flex flex-col items-center">
          <div className="w-20 h-20 rounded-full border-4 border-emerald-500 flex items-center justify-center mb-6">
            <CheckCircle2 size={36} className="text-emerald-400" />
          </div>
          <p className="text-slate-100 font-semibold mb-1">Record Successfully Stored on Blockchain</p>
          <p className="text-xs text-slate-500 mb-6">Your verification record is now tamper-proof and publicly verifiable.</p>
          <div className="w-full text-left text-xs bg-slate-900/60 rounded-xl p-4 border border-slate-800 space-y-2 mb-6">
            <div className="flex justify-between"><span className="text-slate-500">Tx Hash</span><span className="text-slate-300">0x7a9b8c...d4e156</span></div>
            <div className="flex justify-between"><span className="text-slate-500">Block Number</span><span className="text-slate-300">51124567</span></div>
            <div className="flex justify-between"><span className="text-slate-500">Status</span><span className="text-emerald-400">Success</span></div>
          </div>
          <div className="flex gap-3 w-full">
            <GhostButton className="flex-1"><ExternalLink size={13} /> View on Polygonscan</GhostButton>
            <PrimaryButton onClick={onNext} className="flex-1">View Certificate</PrimaryButton>
          </div>
        </div>
      </Panel>
    </div>
  );
}
