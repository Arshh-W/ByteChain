import React from "react";
import { Bell, Settings, CheckCircle2 } from "lucide-react";

export function Panel({ children, className = "", style = {} }) {
  return (
    <div
      className={`rounded-2xl border border-slate-800 ${className}`}
      style={{ background: "linear-gradient(180deg,#11131f,#0b0d16)", ...style }}
    >
      {children}
    </div>
  );
}

export function PanelHeader({ step, title, subtitle, icon: Icon }) {
  return (
    <div className="flex items-start justify-between px-6 pt-5 pb-4 border-b border-slate-800">
      <div>
        <div className="flex items-center gap-2 text-slate-100 font-semibold tracking-wide text-sm">
          {step && (
            <span
              className="text-xs font-bold px-1.5 py-0.5 rounded"
              style={{ background: "linear-gradient(135deg,#a855f7,#3b82f6)" }}
            >
              {step}
            </span>
          )}
          {Icon && <Icon size={16} className="text-slate-400" />}
          <span className="uppercase text-[13px]">{title}</span>
        </div>
        {subtitle && <p className="text-xs text-slate-500 mt-1">{subtitle}</p>}
      </div>
      <div className="flex items-center gap-3 text-slate-500">
        <Bell size={16} />
        <Settings size={16} />
        <div
          className="w-6 h-6 rounded-full flex items-center justify-center"
          style={{ background: "linear-gradient(135deg,#a855f7,#22d3ee)" }}
        >
          <CheckCircle2 size={13} className="text-white" />
        </div>
      </div>
    </div>
  );
}
