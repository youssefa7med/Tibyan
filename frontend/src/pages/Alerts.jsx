import { postJSON } from "../api";

export default function Alerts({ tick }) {
  const alerts = tick?.alerts || [];

  return (
    <div className="max-w-6xl mx-auto px-4 py-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-white font-bold text-xl">Alerts</div>
          <div className="text-white/60 text-sm">Real-time feed + test telegram button</div>
        </div>
        <button
          onClick={() => postJSON("/api/alerts/test-telegram")}
          className="px-4 py-2 rounded-xl bg-brand-500 text-black font-bold"
        >
          Send Test Telegram
        </button>
      </div>

      <div className="card p-4">
        <div className="space-y-2 max-h-[520px] overflow-auto pr-1">
          {alerts.map(a => (
            <div key={a.id} className="rounded-xl bg-white/5 border border-white/10 p-4">
              <div className="flex items-center justify-between">
                <div className="text-white font-bold">{a.title}</div>
                <div className="text-white/50 text-xs">{a.time}</div>
              </div>
              <div className="text-white/70 text-sm mt-1">{a.details}</div>
              {a.meta ? (
                <div className="text-white/50 text-xs mt-2">
                  {JSON.stringify(a.meta)}
                </div>
              ) : null}
            </div>
          ))}
          {alerts.length === 0 ? (
            <div className="text-white/50">No alerts yet. Start monitoring.</div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
