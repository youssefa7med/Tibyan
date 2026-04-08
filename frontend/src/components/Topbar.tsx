interface TopbarProps {
  page: string;
  setPage: (page: string) => void;
}

export default function Topbar({ page, setPage }: TopbarProps) {
  const tabs = [
    ["Dashboard", "dashboard"],
    ["Live Monitor", "live"],
    ["Alerts", "alerts"],
    ["Logs", "logs"],
    ["Settings", "settings"],
  ];

  return (
    <div className="sticky top-0 z-30 backdrop-blur-md bg-ink-900/80 border-b border-white/10 shadow-lg">
      <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-brand-500/30 to-brand-400/20 border border-brand-500/40 flex items-center justify-center shadow-lg">
            <span className="text-brand-300 font-black text-lg">PPE</span>
          </div>
          <div>
            <div className="text-white font-bold leading-tight text-lg">PPE Safety Monitoring</div>
            <div className="text-white/60 text-xs">AI-Enhanced • Production Ready</div>
          </div>
        </div>

        <div className="flex gap-2">
          <button
            onClick={() => setPage("welcome")}
            className="px-3 py-2 rounded-xl text-sm font-semibold bg-white/5 text-white/80 border border-white/10 hover:bg-white/10 transition-all"
          >
            📖 Docs
          </button>
          {tabs.map(([label, key]) => {
            const active = page === key;
            return (
              <button
                key={key}
                onClick={() => setPage(key)}
                className={[
                  "px-3 py-2 rounded-xl text-sm font-semibold border transition-all",
                  active
                    ? "bg-brand-500 text-black border-brand-400 shadow-lg shadow-brand-500/30"
                    : "bg-white/5 text-white/80 border-white/10 hover:bg-white/10",
                ].join(" ")}
              >
                {label}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}


