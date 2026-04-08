export function StatusBadge({ status }) {
  if (status === "SAFE") return <span className="badge bg-green-500/15 text-green-300 border border-green-500/30">SAFE</span>;
  if (status === "CHECK") return <span className="badge bg-brand-500/15 text-brand-200 border border-brand-400/30">CHECK</span>;
  return <span className="badge bg-red-500/15 text-red-300 border border-red-500/30">UNSAFE</span>;
}
