import React from "react";
import { Info } from "lucide-react";
import { Panel, PanelHeader } from "../components/Panel";
import { PrimaryButton } from "../components/Buttons";
import RadialScore from "../components/RadialScore";

export default function ResultsPage({ onNext, analysisResult }) {
  if (!analysisResult) {
    return (
      <div className="p-6">
        <Panel>
          <PanelHeader
            step="03"
            title="Analysis Result"
            subtitle="No analysis result available"
          />
          <p className="p-8 text-sm text-slate-500">
            Upload a file and complete an analysis to view results.
          </p>
        </Panel>
      </div>
    );
  }

  const confidence = Number(analysisResult.confidence_score);
  const confidencePercent = Number.isFinite(confidence)
    ? Math.round((confidence <= 1 ? confidence * 100 : confidence) * 10) / 10
    : null;
  const hasPrediction =
    typeof analysisResult.prediction === "string" &&
    (analysisResult.prediction === "REAL" ||
      analysisResult.prediction === "FAKE");
  const resultLabel = hasPrediction
    ? analysisResult.prediction
    : analysisResult.is_tampered
      ? "Likely tampered"
      : "No tampering detected";
  const resultColor =
    hasPrediction
      ? analysisResult.prediction === "FAKE"
        ? "#fb7185"
        : "#22d3ee"
      : analysisResult.is_tampered
        ? "#fb7185"
        : "#22d3ee";

  const fakePercent =
    analysisResult.fake_probability !== undefined
      ? Math.round(Number(analysisResult.fake_probability) * 1000) / 10
      : null;
  const realPercent =
    analysisResult.real_probability !== undefined
      ? Math.round(Number(analysisResult.real_probability) * 1000) / 10
      : null;

  return (
    <div className="grid grid-cols-3 gap-6 p-6">
      <div className="col-span-2">
        <Panel>
          <PanelHeader
            step="03"
            title="Analysis Result"
            subtitle="Analysis Summary"
          />
          <div className="p-8 grid md:grid-cols-2 gap-8">
            <div className="flex flex-col items-center justify-center">
              <RadialScore
                value={confidencePercent || 0}
                color={resultColor}
                label={resultLabel.toUpperCase()}
                sub="API ANALYSIS"
              />
            </div>
            <div>
              <p className="text-xs font-semibold text-slate-300 mb-3">
                API Analysis
              </p>
              <div className="space-y-3 text-xs">
                <p className="text-slate-500">
                  File:{" "}
                  <span className="text-slate-300">
                    {analysisResult.filename}
                  </span>
                </p>
                <p className="text-slate-500">
                  Confidence:{" "}
                  <span className="text-slate-300">
                    {confidencePercent === null
                      ? "Unavailable"
                      : `${confidencePercent}%`}
                  </span>
                </p>
                {hasPrediction && (
                  <>
                    <p className="text-slate-500">
                      Prediction:{" "}
                      <span
                        className="font-semibold"
                        style={{ color: resultColor }}
                      >
                        {analysisResult.prediction}
                      </span>
                    </p>
                    {fakePercent !== null && (
                      <p className="text-slate-500">
                        Fake probability:{" "}
                        <span className="text-slate-300">
                          {fakePercent}%
                        </span>
                      </p>
                    )}
                    {realPercent !== null && (
                      <p className="text-slate-500">
                        Real probability:{" "}
                        <span className="text-slate-300">
                          {realPercent}%
                        </span>
                      </p>
                    )}
                    {typeof analysisResult.face_detected === "boolean" && (
                      <p className="text-slate-500">
                        Face detected:{" "}
                        <span className="text-slate-300">
                          {analysisResult.face_detected ? "Yes" : "No"}
                          {analysisResult.fallback_used
                            ? " (full-image fallback)"
                            : ""}
                        </span>
                      </p>
                    )}
                    {typeof analysisResult.threshold === "number" && (
                      <p className="text-slate-500">
                        Threshold:{" "}
                        <span className="text-slate-300">
                          {analysisResult.threshold}
                        </span>
                      </p>
                    )}
                  </>
                )}
                <p className="text-slate-500">
                  SHA-256:{" "}
                  <span className="text-slate-300 break-all">
                    {analysisResult.sha256_hash || "Unavailable"}
                  </span>
                </p>
              </div>
            </div>
          </div>
          <div className="px-8 pb-8">
            <p className="text-xs font-semibold text-slate-300 mb-2">
              Timeline Heatmap
            </p>
            <div className="flex gap-1 h-16 items-end">
              {Array.from({ length: 40 }).map((_, i) => {
                const h = 20 + Math.abs(Math.sin(i / 3)) * 70;
                return (
                  <div
                    key={i}
                    className="flex-1 rounded-t"
                    style={{
                      height: `${h}%`,
                      background: h > 60 ? "#fb7185" : "#3f2230",
                    }}
                  />
                );
              })}
            </div>
          </div>
        </Panel>
      </div>
      <div className="flex flex-col gap-6">
        <Panel className="p-5">
          <p className="text-xs font-semibold text-slate-300 mb-3">Findings</p>
          <ul className="space-y-2 text-xs text-slate-500">
            {hasPrediction ? (
              <>
                <li className="flex gap-2">
                  <Info size={13} className="mt-0.5 shrink-0" style={{ color: resultColor }} />
                  <span>
                    Deepfake classifier predicts{" "}
                    <span className="text-slate-300">
                      {analysisResult.prediction}
                    </span>
                    {fakePercent !== null && (
                      <>
                        {" "}with <span className="text-slate-300">{fakePercent}%</span> fake probability.
                      </>
                    )}
                  </span>
                </li>
                {typeof analysisResult.face_detected === "boolean" && (
                  <li className="flex gap-2">
                    <Info size={13} className="text-slate-500 mt-0.5 shrink-0" />
                    <span>
                      Face detection:{" "}
                      <span className="text-slate-300">
                        {analysisResult.face_detected
                          ? "Detected"
                          : "No face found"}
                      </span>
                      {analysisResult.fallback_used
                        ? " — classifier used the full image as fallback."
                        : "."}
                    </span>
                  </li>
                )}
              </>
            ) : (
              <li className="flex gap-2">
                <Info size={13} className="text-slate-500 mt-0.5 shrink-0" />
                Detailed findings are not provided by the current API.
              </li>
            )}
          </ul>
        </Panel>
        <Panel className="p-5">
          <p className="text-xs font-semibold text-slate-300 mb-2">
            Recommendation
          </p>
          <p className="text-xs text-slate-500 mb-4">
            {resultLabel}. Blockchain verification is not connected to the
            current backend.
          </p>
          <PrimaryButton onClick={onNext} className="w-full">
            Proceed to Verify
          </PrimaryButton>
        </Panel>
      </div>
    </div>
  );
}
