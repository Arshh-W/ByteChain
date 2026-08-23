import React, { useEffect, useState } from "react";
import { ChevronRight } from "lucide-react";
import { Panel, PanelHeader } from "../components/Panel";
import { PrimaryButton } from "../components/Buttons";
import RadialScore from "../components/RadialScore";
import { PIPELINE_STEPS } from "../data/mockData";

export default function AnalysisPage({ onNext }) {
  const [pct, setPct] = useState(12);
  useEffect(() => {
    const id = setInterval(() => setPct((p) => (p < 78 ? p + 3 : p)), 180);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="grid grid-cols-3 gap-6 p-6">
      <div className="col-span-2">
        <Panel>
          <PanelHeader step="02" title="AI Analysis" subtitle="Analyzing frames and patterns" />
          <div className="p-8 flex flex-col items-center">
            <RadialScore value={pct} color="#3b82f6" label="ANALYZING" sub="This may take a few seconds" />
            <p className="text-xs text-slate-500 mt-6 mb-2 self-start">Live Frame Analysis</p>
            <div className="flex gap-2 w-full">
              {[0, 1, 2, 3, 4, 5].map((i) => (
                <div key={i}
                  className={`h-16 flex-1 rounded-lg border ${i === 2 ? "border-purple-500" : "border-slate-800"}`}
                  style={{ background: "linear-gradient(135deg,#1e2233,#11131f)" }}
                />
              ))}
            </div>
            <div className="flex justify-end w-full mt-6">
              <PrimaryButton onClick={onNext}>View Results <ChevronRight size={14} className="inline" /></PrimaryButton>
            </div>
          </div>
        </Panel>
      </div>
      <Panel className="p-5 h-fit">
        <p className="text-xs font-semibold text-slate-300 mb-4">Analysis Pipeline</p>
        <ul className="space-y-4">
          {PIPELINE_STEPS.map((s) => (
            <li key={s.label} className="flex items-center justify-between text-xs">
              <span className={s.status === "pending" ? "text-slate-600" : "text-slate-300"}>{s.label}</span>
              <span className={
                s.status === "done" ? "text-emerald-400" :
                s.status === "active" ? "text-blue-400" : "text-slate-600"
              }>
                {s.status === "done" ? "Completed" : s.status === "active" ? "In Progress" : "Pending"}
              </span>
            </li>
          ))}
        </ul>
      </Panel>
    </div>
  );
}
//analysis page with radial score and pipeline steps, with a button to view results