import React from "react";
import { ShieldCheck } from "lucide-react";

export default function Logo({ size = 28 }) {
  return (
    <div className="flex items-center gap-2">
      <div
        className="flex items-center justify-center rounded-lg font-bold text-white"
        style={{
          width: size, height: size,
          background: "linear-gradient(135deg,#a855f7,#3b82f6)",
        }}
      >
        <ShieldCheck size={size * 0.62} />
      </div>
      <span className="font-semibold tracking-tight text-slate-100">ByteChain Verify</span>
    </div>
  );
}
