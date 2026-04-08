export default function KPI({ title, value, hint, tone = "neutral", icon }) {
  const toneCls =
    tone === "good"
      ? "text-green-400"
      : tone === "warn"
      ? "text-brand-400"
      : tone === "bad"
      ? "text-red-400"
      : "text-white";

  const bgCls =
    tone === "good"
      ? "bg-green-500/10 border-green-500/30"
      : tone === "warn"
      ? "bg-yellow-500/10 border-yellow-500/30"
      : tone === "bad"
      ? "bg-red-500/10 border-red-500/30"
      : "bg-white/5 border-white/10";

  return (
    <div className={`card p-4 ${bgCls} transition-all hover:scale-105 hover:shadow-lg`}>
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <div className="text-white/60 text-xs font-semibold uppercase tracking-wide">{title}</div>
          <div className={`text-3xl font-black mt-2 ${toneCls}`}>{value}</div>
          {hint ? <div className="text-white/50 text-xs mt-1">{hint}</div> : null}
        </div>
        {icon && <div className="text-3xl opacity-50">{icon}</div>}
      </div>
    </div>
  );
}
