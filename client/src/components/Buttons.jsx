import React from "react";

export function PrimaryButton({
  children,
  onClick,
  className = "",
  disabled = false,
}) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`px-5 py-2.5 rounded-xl text-sm font-semibold text-white shadow-lg ${className}`}
      style={{ background: "linear-gradient(90deg,#a855f7,#3b82f6)" }}
    >
      {children}
    </button>
  );
}

export function GhostButton({
  children,
  onClick,
  className = "",
  disabled = false,
}) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`px-5 py-2.5 rounded-xl text-sm font-semibold text-slate-200 border border-slate-700 flex items-center gap-2 justify-center ${className}`}
    >
      {children}
    </button>
  );
}
