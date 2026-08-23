import React from "react";

export default function RadialScore({ value, size = 170, color = "#fb7185", label, sub }) {
  const r = 66;
  const c = 2 * Math.PI * r;
  const offset = c - (value / 100) * c;
  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox="0 0 160 160">
        <circle cx="80" cy="80" r={r} stroke="#1e2233" strokeWidth="12" fill="none" />
        <circle
          cx="80" cy="80" r={r} stroke={color} strokeWidth="12" fill="none"
          strokeDasharray={c} strokeDashoffset={offset} strokeLinecap="round"
          transform="rotate(-90 80 80)"
        />
      </svg>
      <div className="absolute flex flex-col items-center">
        <span className="text-3xl font-bold text-slate-100">{value}%</span>
        {label && <span className="text-[11px] font-semibold tracking-wide mt-1" style={{ color }}>{label}</span>}
        {sub && <span className="text-[10px] text-slate-500">{sub}</span>}
      </div>
    </div>
  );
}
