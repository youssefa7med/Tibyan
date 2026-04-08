import { useEffect, useState } from "react";
import Topbar from "./components/Topbar";
import Welcome from "./pages/Welcome";
import Features from "./pages/Features";
import About from "./pages/About";
import Info from "./pages/Info";
import Dashboard from "./pages/Dashboard";
import Live from "./pages/Live";
import Alerts from "./pages/Alerts";
import Logs from "./pages/Logs";
import Settings from "./pages/Settings";
import { getJSON } from "./api";
import { useEvents } from "./hooks/useEvents";
import { WavyBackground } from "./components/ui/wavy-background";

export default function App() {
  const [page, setPage] = useState("welcome");
  const [stats, setStats] = useState(null);
  const { connected, tick } = useEvents();

  useEffect(() => {
    const t = setInterval(async () => {
      try {
        const s = await getJSON("/api/stats");
        setStats(s);
      } catch {}
    }, 1500);
    return () => clearInterval(t);
  }, []);

  const handleGetStarted = () => {
    setPage("dashboard");
  };

  const handleBackToWelcome = () => {
    setPage("welcome");
  };

  if (page === "welcome") {
    return <Welcome onGetStarted={handleGetStarted} setPage={setPage} />;
  }

  if (page === "features") {
    return <Features onBack={handleBackToWelcome} />;
  }

  if (page === "about") {
    return <About onBack={handleBackToWelcome} />;
  }

  if (page === "info") {
    return <Info onBack={handleBackToWelcome} />;
  }

  return (
    <WavyBackground
      colors={["#f97316", "#ea580c", "#c2410c", "#fb923c", "#fdba74"]}
      waveWidth={50}
      backgroundFill="rgba(11, 18, 32, 0.9)"
      blur={8}
      speed="slow"
      waveOpacity={0.15}
      containerClassName="min-h-screen"
    >
      <div className="min-h-screen relative z-10">
        <Topbar page={page} setPage={setPage} />

        <div className="max-w-6xl mx-auto px-4 pt-4">
          <div className="card p-3 flex items-center justify-between">
            <div className="text-white/80 text-sm">
              Backend: <span className="text-white font-semibold">http://localhost:8000</span>{" "}
              • WS: <span className={`font-semibold ${connected ? "text-green-400" : "text-red-400"}`}>
                {connected ? "● Connected" : "○ Disconnected"}
              </span>
            </div>
            <div className="text-white/60 text-xs">
              Tip: Go to <span className="text-brand-300 font-bold">Live Monitor</span> and click <span className="text-brand-300 font-bold">Start</span>
            </div>
          </div>
        </div>

        {page === "dashboard" && <Dashboard stats={stats} tick={tick} />}
        {page === "live" && <Live tick={tick} />}
        {page === "alerts" && <Alerts tick={tick} />}
        {page === "logs" && <Logs />}
        {page === "settings" && <Settings />}
      </div>
    </WavyBackground>
  );
}
