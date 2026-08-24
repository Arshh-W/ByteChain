import React, { useState } from "react";
import { Wallet } from "lucide-react";
import Logo from "./Logo";
import { NAV_ITEMS } from "../data/mockData";

export default function Sidebar({ page, setPage }) {
  const [walletStatus, setWalletStatus] = useState("Not connected");

  const connectWallet = async () => {
    if (!window.ethereum) {
      setWalletStatus("Wallet unavailable");
      return;
    }

    try {
      const accounts = await window.ethereum.request({
        method: "eth_requestAccounts",
      });
      setWalletStatus(
        accounts[0]
          ? `${accounts[0].slice(0, 6)}...${accounts[0].slice(-4)}`
          : "Not connected",
      );
    } catch {
      setWalletStatus("Connection cancelled");
    }
  };

  return (
    <div
      className="w-48 shrink-0 border-r border-slate-800 flex flex-col py-5 px-3 gap-1"
      style={{ background: "#0b0d16" }}
    >
      <div className="px-2 pb-5">
        <Logo size={24} />
      </div>
      {NAV_ITEMS.map((item) => {
        const active = page === item.key;
        const Icon = item.icon;
        return (
          <button
            key={item.key}
            onClick={() => setPage(item.key)}
            className={`flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-colors ${
              active ? "text-white" : "text-slate-500 hover:text-slate-300"
            }`}
            style={
              active
                ? {
                    background:
                      "linear-gradient(90deg,rgba(168,85,247,0.25),rgba(59,130,246,0.15))",
                  }
                : {}
            }
          >
            <Icon size={16} />
            {item.label}
          </button>
        );
      })}
      <div className="mt-auto px-2 pt-4">
        <button
          onClick={connectWallet}
          className="w-full text-xs text-left px-3 py-2 rounded-lg border border-slate-800 text-slate-400 flex items-center gap-2"
        >
          <Wallet size={14} /> {walletStatus}
        </button>
        <p className="text-[10px] text-slate-600 mt-2 px-1">Polygon Amoy</p>
      </div>
    </div>
  );
}
