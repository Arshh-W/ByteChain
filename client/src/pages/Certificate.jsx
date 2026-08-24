import React, { useState } from "react";
import { ShieldCheck, Download, Share2 } from "lucide-react";
import { Panel, PanelHeader } from "../components/Panel";
import { PrimaryButton, GhostButton } from "../components/Buttons";

export default function CertificatePage({ onNext }) {
  const [message, setMessage] = useState("");

  const downloadCertificate = () => {
    setMessage(
      "Use your browser print dialog to save this certificate as a PDF.",
    );
    window.print();
  };

  const shareCertificate = async () => {
    const shareData = {
      title: "ByteChain Verification Certificate",
      text: "Image verification certificate from ByteChain Verify.",
      url: window.location.href,
    };

    try {
      if (navigator.share) {
        await navigator.share(shareData);
        setMessage("Certificate shared.");
      } else if (navigator.clipboard) {
        await navigator.clipboard.writeText(window.location.href);
        setMessage("Certificate link copied to the clipboard.");
      } else {
        setMessage("Sharing is not supported in this browser.");
      }
    } catch {
      setMessage("Sharing was cancelled.");
    }
  };

  return (
    <div className="p-6 flex justify-center">
      <Panel className="max-w-xl w-full">
        <PanelHeader step="06" title="Certificate" />
        <div className="p-8">
          <div
            className="rounded-2xl p-8 border"
            style={{
              borderColor: "#7c3aed55",
              background: "linear-gradient(160deg,#171325,#0b0d16)",
            }}
          >
            <div className="flex items-center gap-3 mb-6">
              <div
                className="w-10 h-10 rounded-xl flex items-center justify-center"
                style={{
                  background: "linear-gradient(135deg,#a855f7,#3b82f6)",
                }}
              >
                <ShieldCheck size={20} className="text-white" />
              </div>
              <div>
                <p className="font-semibold text-slate-100 leading-tight">
                  ByteChain Verify
                </p>
                <p className="text-[11px] text-slate-500 leading-tight">
                  Verification Certificate
                </p>
              </div>
            </div>
            <p className="text-xs text-slate-400 mb-6">
              This certifies that the image file has been analyzed and verified
              on Aug 23, 2026.
            </p>
            <div className="grid grid-cols-2 gap-y-3 text-xs mb-6">
              <div>
                <p className="text-slate-500">File Name</p>
                <p className="text-slate-200">interview_portrait.jpg</p>
              </div>
              <div>
                <p className="text-slate-500">Authenticity Score</p>
                <p className="text-rose-400">24.8%</p>
              </div>
              <div>
                <p className="text-slate-500">Result</p>
                <p className="text-rose-400">High Probability Deepfake</p>
              </div>
              <div>
                <p className="text-slate-500">Verification ID</p>
                <p className="text-slate-200">BCV-2026-08-23-142536</p>
              </div>
              <div>
                <p className="text-slate-500">Blockchain Tx</p>
                <p className="text-slate-200">0x7a9b8c...d4e156</p>
              </div>
              <div>
                <p className="text-slate-500">Network</p>
                <p className="text-slate-200">Polygon Amoy</p>
              </div>
            </div>
            <div className="flex justify-center">
              <div className="w-24 h-24 rounded-lg grid grid-cols-4 grid-rows-4 gap-0.5 p-2 bg-white">
                {Array.from({ length: 16 }).map((_, i) => (
                  <div
                    key={i}
                    className={
                      (i * 7) % 3 === 0 ? "bg-black rounded-[1px]" : ""
                    }
                  />
                ))}
              </div>
            </div>
          </div>
          <div className="flex gap-3 mt-6">
            <GhostButton onClick={downloadCertificate} className="flex-1">
              <Download size={14} /> Download PDF
            </GhostButton>
            <GhostButton onClick={shareCertificate} className="flex-1">
              <Share2 size={14} /> Share Certificate
            </GhostButton>
            <PrimaryButton onClick={onNext} className="flex-1">
              Go to Dashboard
            </PrimaryButton>
          </div>
          {message && (
            <p role="status" className="text-xs text-slate-500 mt-4">
              {message}
            </p>
          )}
        </div>
      </Panel>
    </div>
  );
}
//certificate page showing verification details, authenticity score, and a QR code, with buttons to download or share the certificate
