import React, { useState } from "react";
import Sidebar from "./components/Sidebar";
import Landing from "./pages/Landing";
import UploadPage from "./pages/Upload";
import AnalysisPage from "./pages/Analysis";
import ResultsPage from "./pages/Results";
import BlockchainPage from "./pages/Blockchain";
import SuccessPage from "./pages/Success";
import CertificatePage from "./pages/Certificate";
import DashboardPage from "./pages/Dashboard";

export default function App() {
  const [page, setPage] = useState("landing");
  const [analysisResult, setAnalysisResult] = useState(null);

  if (page === "landing") return <Landing goApp={setPage} />;

  const flow = [
    "upload",
    "analysis",
    "results",
    "blockchain",
    "success",
    "certificate",
    "dashboard",
  ];
  const next = () => {
    const i = flow.indexOf(page);
    setPage(flow[Math.min(i + 1, flow.length - 1)]);
  };

  return (
    <div className="min-h-screen flex" style={{ background: "#05060c" }}>
      <Sidebar page={page} setPage={setPage} />
      <div className="flex-1 overflow-auto">
        {page === "upload" && (
          <UploadPage
            onNext={next}
            onAnalyzed={setAnalysisResult}
            onNavigate={setPage}
          />
        )}
        {page === "analysis" && <AnalysisPage onNext={next} />}
        {page === "results" && (
          <ResultsPage onNext={next} analysisResult={analysisResult} />
        )}
        {page === "blockchain" && <BlockchainPage onNext={next} />}
        {page === "success" && <SuccessPage onNext={next} />}
        {page === "certificate" && <CertificatePage onNext={next} />}
        {page === "dashboard" && <DashboardPage onNavigate={setPage} />}
      </div>
    </div>
  );
}
