import { useEffect, useState } from "react";
import { getJSON } from "../api";
import { useEvents } from "../hooks/useEvents";

export default function Logs() {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const { connected, logs } = useEvents();

  async function load() {
    const r = await getJSON("/api/logs?limit=50&offset=0");
    setItems(r.items || []);
    setTotal(r.total || 0);
  }

  // Load initial logs
  useEffect(() => { load(); }, []);

  // Update logs in real-time from WebSocket
  useEffect(() => {
    if (logs && logs.length > 0) {
      setItems(logs.slice(0, 50)); // Show latest 50 entries
      setTotal(logs.length);
    }
  }, [logs]);

  return (
    <div className="max-w-6xl mx-auto px-4 py-6 space-y-4">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="text-white font-bold text-xl">Logs</div>
          <div className="text-white/60 text-sm">
            CSV logger (newest first). Total rows: {total}
            {connected ? (
              <span className="ml-2 text-brand-400">● Real-time</span>
            ) : (
              <span className="ml-2 text-red-400">○ Disconnected</span>
            )}
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          <a href="http://localhost:8000/api/reports/safety_log.csv" className="px-3 py-2 rounded-xl bg-white/10 text-white text-sm font-semibold border border-white/10 hover:bg-white/20 transition-all whitespace-nowrap">
            📥 Safety Log
          </a>
          <a href="http://localhost:8000/api/reports/safety_summary.csv" className="px-3 py-2 rounded-xl bg-white/10 text-white text-sm font-semibold border border-white/10 hover:bg-white/20 transition-all whitespace-nowrap">
            📥 Summary
          </a>
          <button onClick={load} className="px-4 py-2 rounded-xl bg-brand-500 text-black text-sm font-bold hover:bg-brand-400 transition-all">
            🔄 Refresh
          </button>
        </div>
      </div>

      <div className="card p-4 overflow-x-auto max-h-[calc(100vh-250px)]">
        <table className="min-w-full text-sm">
          <thead className="text-white/70 sticky top-0 bg-ink-800/90 backdrop-blur-sm">
            <tr className="border-b border-white/10">
              {["timestamp","frame_id","person_id","helmet","vest","status","unsafe_counter"].map(h => (
                <th key={h} className="text-left py-2 px-2 font-semibold whitespace-nowrap">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="text-white/80">
            {items.map((r, idx) => (
              <tr key={idx} className="border-b border-white/5 hover:bg-white/5">
                <td className="py-2 px-2 text-white/60 whitespace-nowrap">{r.timestamp}</td>
                <td className="py-2 px-2">{r.frame_id}</td>
                <td className="py-2 px-2">{r.person_id}</td>
                <td className="py-2 px-2">{String(r.helmet)}</td>
                <td className="py-2 px-2">{String(r.vest)}</td>
                <td className="py-2 px-2 font-bold">{r.status}</td>
                <td className="py-2 px-2">{r.unsafe_counter}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {items.length === 0 ? <div className="text-white/50 p-4 text-center">No data yet.</div> : null}
      </div>
    </div>
  );
}
