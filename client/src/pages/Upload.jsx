import React, { useRef, useState } from "react";
import {
  UploadCloud,
  CheckCircle2,
  PlayCircle,
  ChevronRight,
} from "lucide-react";
import { Panel, PanelHeader } from "../components/Panel";
import { PrimaryButton } from "../components/Buttons";
import { RECENT_UPLOADS } from "../data/mockData";
import { analyzeFile } from "../api/client";

export default function UploadPage({ onNext, onAnalyzed }) {
  const fileInput = useRef(null);
  const [file, setFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [hasSubmitted, setHasSubmitted] = useState(false);

  const selectFile = (selectedFile) => {
    setFile(selectedFile || null);
    setError(null);
    setHasSubmitted(false);
  };

  const submitFile = async () => {
    if (!file) {
      setError("Choose a video before starting the analysis.");
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const result = await analyzeFile(file);
      onAnalyzed(result);
      setHasSubmitted(true);
    } catch (requestError) {
      setError(requestError.message || "The analysis could not be completed.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-3 gap-6 p-6">
      <div className="col-span-2">
        <Panel>
          <PanelHeader
            step="01"
            title="Upload Video"
            subtitle="Upload your video for authenticity analysis"
          />
          <div className="p-8">
            <div
              className="border-2 border-dashed border-slate-700 rounded-2xl flex flex-col items-center justify-center py-16 cursor-pointer hover:border-purple-500 transition-colors"
              onClick={() => fileInput.current?.click()}
            >
              <div
                className="w-14 h-14 rounded-2xl flex items-center justify-center mb-4"
                style={{
                  background: "linear-gradient(135deg,#a855f7,#3b82f6)",
                }}
              >
                <UploadCloud size={26} className="text-white" />
              </div>
              <p className="text-slate-300 text-sm mb-1">
                Drag & drop your video here
              </p>
              <p className="text-slate-600 text-xs mb-5">or</p>
              <input
                type="file"
                ref={fileInput}
                className="hidden"
                accept="video/mp4,video/quicktime,video/x-msvideo"
                onChange={(e) => selectFile(e.target.files?.[0])}
              />
              <PrimaryButton onClick={() => fileInput.current?.click()}>
                Choose File
              </PrimaryButton>
              <p className="text-[11px] text-slate-600 mt-5">
                MP4, MOV, AVI up to 500MB
              </p>
              <p className="text-[11px] text-slate-600">
                Best results with videos &lt; 5 minutes
              </p>
            </div>
            {file && (
              <div className="mt-5 flex items-center justify-between text-sm bg-slate-900/60 rounded-xl px-4 py-3 border border-slate-800">
                <span className="text-slate-300">{file.name}</span>
                <span className="text-emerald-400 text-xs">
                  {hasSubmitted ? "Analyzed" : "Ready"}
                </span>
              </div>
            )}
            {error && (
              <p role="alert" className="mt-4 text-xs text-rose-400">
                {error}
              </p>
            )}
            {!file && !error && (
              <p className="mt-4 text-xs text-slate-600">No file selected.</p>
            )}
            {hasSubmitted && (
              <p className="mt-4 text-xs text-emerald-400">
                Analysis complete. Continue to review the result.
              </p>
            )}
            <div className="flex justify-end mt-6">
              <PrimaryButton
                onClick={hasSubmitted ? onNext : submitFile}
                disabled={isLoading}
              >
                {isLoading
                  ? "Analyzing..."
                  : hasSubmitted
                    ? "View Results"
                    : "Analyze Video"}
                {!isLoading && <ChevronRight size={14} className="inline" />}
              </PrimaryButton>
            </div>
          </div>
        </Panel>
      </div>

      <div className="flex flex-col gap-6">
        <Panel className="p-5">
          <p className="text-xs font-semibold text-slate-300 mb-3">
            Tips for best analysis
          </p>
          <ul className="space-y-2 text-xs text-slate-500">
            {[
              "Use original, unedited file",
              "Good lighting conditions",
              "Front-facing subject",
              "Minimum 720p resolution",
            ].map((t) => (
              <li key={t} className="flex items-center gap-2">
                <CheckCircle2 size={13} className="text-emerald-400" />
                {t}
              </li>
            ))}
          </ul>
        </Panel>
        <Panel className="p-5">
          <div className="flex items-center justify-between mb-3">
            <p className="text-xs font-semibold text-slate-300">
              Recent Uploads
            </p>
            <span className="text-[11px] text-purple-400">View all</span>
          </div>
          <ul className="space-y-3">
            {RECENT_UPLOADS.map((u) => (
              <li key={u.name} className="flex items-center gap-3 text-xs">
                <div className="w-7 h-7 rounded-lg bg-rose-500/10 flex items-center justify-center text-rose-400">
                  <PlayCircle size={14} />
                </div>
                <div>
                  <p className="text-slate-300">{u.name}</p>
                  <p className="text-slate-600 text-[10px]">{u.meta}</p>
                </div>
              </li>
            ))}
          </ul>
        </Panel>
      </div>
    </div>
  );
}
