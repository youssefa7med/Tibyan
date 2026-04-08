import { useState } from "react";
import KPI from "../components/KPI";
import { WavyBackground } from "../components/ui/wavy-background";
import RadialOrbitalTimeline from "../components/ui/radial-orbital-timeline";
import { Calendar, Code, FileText, User, Clock, Shield, AlertTriangle, CheckCircle } from "lucide-react";

interface DashboardProps {
  stats: any;
  tick: any;
}

export default function Dashboard({ stats, tick }: DashboardProps) {
  const [showTimeline, setShowTimeline] = useState(false);
  const counts = stats?.counts || tick?.counts || { total: 0, safe: 0, check: 0, unsafe: 0 };
  const fps = stats?.fps ?? tick?.fps ?? 0;
  const safety = stats?.safety_percentage ?? 0;
  const enhanced = stats?.enhanced_metrics || tick?.enhanced_metrics || {};

  // Create timeline data from system stats
  const timelineData = [
    {
      id: 1,
      title: "System Initialized",
      date: "Start",
      content: "Tibyan monitoring system started successfully.",
      category: "System",
      icon: Shield,
      relatedIds: [2],
      status: "completed" as const,
      energy: 100,
    },
    {
      id: 2,
      title: "Detection Active",
      date: "Running",
      content: `Currently monitoring ${counts.total} worker(s) in real-time.`,
      category: "Monitoring",
      icon: CheckCircle,
      relatedIds: [1, 3],
      status: counts.total > 0 ? ("in-progress" as const) : ("pending" as const),
      energy: counts.total > 0 ? 90 : 30,
    },
    {
      id: 3,
      title: "Safety Compliance",
      date: "Live",
      content: `Safety compliance rate: ${safety.toFixed(1)}%. ${counts.safe} safe, ${counts.check} checking, ${counts.unsafe} unsafe.`,
      category: "Safety",
      icon: AlertTriangle,
      relatedIds: [2, 4],
      status: counts.unsafe > 0 ? ("in-progress" as const) : ("completed" as const),
      energy: Math.max(10, 100 - counts.unsafe * 20),
    },
    {
      id: 4,
      title: "AI Processing",
      date: "Active",
      content: `Processing at ${fps.toFixed(1)} FPS. Quality: ${(enhanced.quality_score || 0).toFixed(2)}, Confidence: ${(enhanced.confidence || 0).toFixed(2)}.`,
      category: "AI",
      icon: Code,
      relatedIds: [3, 5],
      status: fps > 0 ? ("in-progress" as const) : ("pending" as const),
      energy: Math.min(100, fps * 10),
    },
    {
      id: 5,
      title: "System Status",
      date: "Now",
      content: "All systems operational. Real-time monitoring active.",
      category: "Status",
      icon: Clock,
      relatedIds: [4],
      status: "completed" as const,
      energy: 100,
    },
  ];

  if (showTimeline) {
    return (
      <div className="fixed inset-0 z-50">
        <WavyBackground
          colors={["#f97316", "#ea580c", "#c2410c", "#fb923c", "#fdba74"]}
          waveWidth={50}
          backgroundFill="rgba(11, 18, 32, 0.95)"
          blur={10}
          speed="fast"
          waveOpacity={0.3}
        >
          <div className="relative z-20 w-full h-full">
            <button
              onClick={() => setShowTimeline(false)}
              className="absolute top-4 right-4 z-30 px-4 py-2 bg-brand-500 text-brand-900 font-bold rounded-lg hover:bg-brand-400 transition-all"
            >
              Close Timeline
            </button>
            <RadialOrbitalTimeline timelineData={timelineData} />
          </div>
        </WavyBackground>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-6 space-y-6 relative z-10">
        {/* Header with Timeline Toggle */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Dashboard</h1>
            <p className="text-white/60">Real-time Safety Monitoring by Tibyan</p>
          </div>
          <button
            onClick={() => setShowTimeline(true)}
            className="px-6 py-3 bg-brand-500 text-brand-900 font-bold rounded-xl hover:bg-brand-400 transition-all shadow-lg hover:shadow-brand-500/50"
          >
            View Timeline →
          </button>
        </div>

        {/* Enhanced KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <KPI title="Total Persons" value={counts.total} icon="👥" />
          <KPI title="Safe" value={counts.safe} tone="good" icon="✅" />
          <KPI title="Check" value={counts.check} tone="warn" icon="⚠️" />
          <KPI title="Unsafe" value={counts.unsafe} tone="bad" icon="🚨" />
          <KPI title="FPS" value={fps.toFixed(1)} hint="Processing speed" icon="⚡" />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Safety Overview - Enhanced */}
          <div className="card p-6 md:col-span-2">
            <div className="flex items-center justify-between mb-4">
              <div>
                <div className="text-white font-bold text-xl">Safety Overview</div>
                <div className="text-white/60 text-sm mt-1">
                  Real-time monitoring with AI-enhanced detection
                </div>
              </div>
              <div className="h-12 w-12 rounded-full bg-brand-500/20 flex items-center justify-center">
                <span className="text-2xl">🛡️</span>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <div className="flex items-center justify-between text-sm text-white/70 mb-2">
                  <span>Safety Compliance Rate</span>
                  <span className="text-brand-300 font-bold text-lg">{safety.toFixed(1)}%</span>
                </div>
                <div className="h-4 rounded-full bg-white/10 overflow-hidden shadow-inner">
                  <div
                    className="h-full bg-gradient-to-r from-brand-500 to-brand-400 transition-all duration-500 shadow-lg"
                    style={{ width: `${Math.min(100, Math.max(0, safety))}%` }}
                  />
                </div>
                <div className="text-white/50 text-xs mt-2">
                  Based on SAFE vs (SAFE+CHECK+UNSAFE) • {counts.total} total workers
                </div>
              </div>

              {/* Enhanced Metrics */}
              {enhanced && Object.keys(enhanced).length > 0 && (
                <div className="grid grid-cols-3 gap-3 pt-4 border-t border-white/10">
                  <div className="text-center">
                    <div className="text-white/60 text-xs mb-1">Quality Score</div>
                    <div className="text-white font-bold">
                      {(enhanced.quality_score || 0).toFixed(2)}
                    </div>
                  </div>
                  <div className="text-center">
                    <div className="text-white/60 text-xs mb-1">Confidence</div>
                    <div className="text-white font-bold">
                      {(enhanced.confidence || 0).toFixed(2)}
                    </div>
                  </div>
                  <div className="text-center">
                    <div className="text-white/60 text-xs mb-1">Occlusions</div>
                    <div className="text-white font-bold">
                      {enhanced.occlusion_count || 0}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Latest Alerts - Enhanced */}
          <div className="card p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <div className="text-white font-bold text-xl">Latest Alerts</div>
                <div className="text-white/60 text-sm mt-1">Most recent system events</div>
              </div>
              <span className="text-2xl">🔔</span>
            </div>
            <div className="mt-3 space-y-2 max-h-80 overflow-auto pr-1">
              {(tick?.alerts || []).slice(0, 8).map((a: any) => {
                const kindColors = {
                  danger: "border-red-500/30 bg-red-500/10",
                  warn: "border-yellow-500/30 bg-yellow-500/10",
                  info: "border-blue-500/30 bg-blue-500/10"
                };
                return (
                  <div
                    key={a.id}
                    className={`rounded-xl border p-3 transition-all hover:scale-[1.02] ${kindColors[a.kind as keyof typeof kindColors] || "border-white/10 bg-white/5"}`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="text-white font-semibold text-sm">{a.title}</div>
                      <div className="text-white/50 text-xs">{a.time}</div>
                    </div>
                    <div className="text-white/70 text-xs mt-1">{a.details}</div>
                  </div>
                );
              })}
              {(!tick?.alerts || tick.alerts.length === 0) ? (
                <div className="text-white/50 text-sm text-center py-4">
                  No alerts yet. Start monitoring to see events.
                </div>
              ) : null}
            </div>
          </div>
        </div>

        {/* Status Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="card p-5 bg-green-500/10 border-green-500/30">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-green-300 font-bold">Safe Workers</div>
                <div className="text-white text-3xl font-black mt-2">{counts.safe}</div>
              </div>
              <span className="text-4xl">✅</span>
            </div>
          </div>
          <div className="card p-5 bg-yellow-500/10 border-yellow-500/30">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-yellow-300 font-bold">Needs Check</div>
                <div className="text-white text-3xl font-black mt-2">{counts.check}</div>
              </div>
              <span className="text-4xl">⚠️</span>
            </div>
          </div>
          <div className="card p-5 bg-red-500/10 border-red-500/30">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-red-300 font-bold">Unsafe Workers</div>
                <div className="text-white text-3xl font-black mt-2">{counts.unsafe}</div>
              </div>
              <span className="text-4xl">🚨</span>
            </div>
          </div>
        </div>
      </div>
  );
}

