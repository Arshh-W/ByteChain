import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import { Panel, PanelHeader } from "../components/Panel";
import { TREND_DATA, DIST_DATA, RECENT_VERIFICATIONS } from "../data/mockData";

export default function DashboardPage({ onNavigate }) {
  const stats = [
    ["Total Verifications", "24", "+12 this month", "text-blue-400"],
    ["Deepfake Detected", "16", "66.7%", "text-rose-400"],
    ["Authentic Images", "8", "33.3%", "text-emerald-400"],
    ["On-Chain Records", "24", "100% Secured", "text-purple-400"],
  ];
  return (
    <div className="p-6">
      <Panel className="mb-6">
        <PanelHeader
          step="07"
          title="Dashboard"
          subtitle="Overview of your verification activity"
        />
        <div className="p-6 grid grid-cols-4 gap-4">
          {stats.map(([label, val, sub, color]) => (
            <div
              key={label}
              className="rounded-xl border border-slate-800 p-4"
              style={{ background: "#0f1120" }}
            >
              <p className="text-[11px] text-slate-500 mb-2">{label}</p>
              <p className="text-2xl font-bold text-slate-100">{val}</p>
              <p className={`text-[11px] mt-1 ${color}`}>{sub}</p>
            </div>
          ))}
        </div>
      </Panel>

      <div className="grid grid-cols-3 gap-6">
        <Panel className="col-span-2 p-5">
          <div className="flex justify-between mb-4">
            <p className="text-xs font-semibold text-slate-300">
              Verification Trend
            </p>
            <span className="text-[11px] text-slate-500">7 Days</span>
          </div>
          <div style={{ width: "100%", height: 200 }}>
            <ResponsiveContainer>
              <LineChart data={TREND_DATA}>
                <XAxis
                  dataKey="day"
                  tick={{ fill: "#64748b", fontSize: 10 }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  tick={{ fill: "#64748b", fontSize: 10 }}
                  axisLine={false}
                  tickLine={false}
                />
                <Tooltip
                  contentStyle={{
                    background: "#11131f",
                    border: "1px solid #1e2233",
                    fontSize: 12,
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="value"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  dot={{ r: 3, fill: "#3b82f6" }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Panel>

        <Panel className="p-5">
          <p className="text-xs font-semibold text-slate-300 mb-4">
            Result Distribution
          </p>
          <div style={{ width: "100%", height: 140 }}>
            <ResponsiveContainer>
              <PieChart>
                <Pie
                  data={DIST_DATA}
                  dataKey="value"
                  innerRadius={40}
                  outerRadius={60}
                  paddingAngle={3}
                >
                  {DIST_DATA.map((d) => (
                    <Cell key={d.name} fill={d.color} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex justify-center gap-4 text-[11px] mt-2">
            {DIST_DATA.map((d) => (
              <span
                key={d.name}
                className="flex items-center gap-1.5 text-slate-400"
              >
                <span
                  className="w-2 h-2 rounded-full"
                  style={{ background: d.color }}
                />
                {d.name} {d.value}%
              </span>
            ))}
          </div>
        </Panel>
      </div>

      <Panel className="mt-6 p-5">
        <div className="flex justify-between mb-4">
          <p className="text-xs font-semibold text-slate-300">
            Recent Verifications
          </p>
          <button
            type="button"
            onClick={() => onNavigate("upload")}
            className="text-[11px] text-purple-400"
          >
            Upload image
          </button>
        </div>
        <ul className="divide-y divide-slate-800">
          {RECENT_VERIFICATIONS.map((v) => (
            <li
              key={v.name}
              className="flex items-center justify-between py-2.5 text-xs"
            >
              <div>
                <p className="text-slate-300">{v.name}</p>
                <p className="text-slate-600 text-[10px]">{v.meta}</p>
              </div>
              <span
                className={
                  v.tone === "rose" ? "text-rose-400" : "text-emerald-400"
                }
              >
                {v.score}
              </span>
            </li>
          ))}
        </ul>
      </Panel>
    </div>
  );
}
//dashboard page showing stats, verification trend, result distribution, and recent verifications
