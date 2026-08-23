import React from "react";
import { Info } from "lucide-react";
import { Panel, PanelHeader } from "../components/Panel";
import { PrimaryButton } from "../components/Buttons";
import RadialScore from "../components/RadialScore";
import { KEY_FINDINGS, NOTES } from "../data/mockData";

export default function ResultsPage({ onNext }) {
  return (
    <div className="grid grid-cols-3 gap-6 p-6">
      <div className="col-span-2">
        <Panel>
          <PanelHeader step="03" title="Analysis Result" subtitle="Analysis Summary" />
          <div className="p-8 grid md:grid-cols-2 gap-8">
            <div className="flex flex-col items-center justify-center">
              <RadialScore value={24.8} color="#fb7185" label="HIGH PROBABILITY" sub="DEEPFAKE" />
            </div>
            <div>
              <p className="text-xs font-semibold text-slate-300 mb-3">Key Findings</p>
              <div className="space-y-3">
                {KEY_FINDINGS.map((f) => (
                  <div key={f.label}>
                    <div className="flex justify-between text-[11px] text-slate-400 mb-1">
                      <span>{f.label}</span><span>{f.value}%</span>
                    </div>
                    <div className="h-1.5 rounded-full bg-slate-800">
                      <div className="h-1.5 rounded-full"
                        style={{ width: `${f.value}%`, background: f.value > 50 ? "#fb7185" : "#22d3ee" }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
          <div className="px-8 pb-8">
            <p className="text-xs font-semibold text-slate-300 mb-2">Timeline Heatmap</p>
            <div className="flex gap-1 h-16 items-end">
              {Array.from({ length: 40 }).map((_, i) => {
                const h = 20 + Math.abs(Math.sin(i / 3)) * 70;
                return <div key={i} className="flex-1 rounded-t"
                  style={{ height: `${h}%`, background: h > 60 ? "#fb7185" : "#3f2230" }} />;
              })}
            </div>
          </div>
        </Panel>
      </div>
      <div className="flex flex-col gap-6">
        <Panel className="p-5">
          <p className="text-xs font-semibold text-slate-300 mb-3">Findings</p>
          <ul className="space-y-2 text-xs text-slate-500">
            {NOTES.map((n) => <li key={n} className="flex gap-2"><Info size={13} className="text-rose-400 mt-0.5 shrink-0" />{n}</li>)}
          </ul>
        </Panel>
        <Panel className="p-5">
          <p className="text-xs font-semibold text-slate-300 mb-2">Recommendation</p>
          <p className="text-xs text-slate-500 mb-4">This video shows strong indicators of manipulation.</p>
          <PrimaryButton onClick={onNext} className="w-full">Proceed to Verify</PrimaryButton>
        </Panel>
      </div>
    </div>
  );
}
