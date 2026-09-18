const LEVEL_BADGE = {
  low: "bg-green-100 text-green-800",
  medium: "bg-yellow-100 text-yellow-800",
  high: "bg-orange-100 text-orange-800",
  critical: "bg-red-100 text-red-800",
};

export default function RiskEventsTable({ events, loading }) {
  if (loading) {
    return <p className="text-sm text-slate-500">Loading risk events...</p>;
  }

  if (!events?.length) {
    return (
      <p className="text-sm text-slate-500">
        No risk events yet. Create an operation and run an assessment.
      </p>
    );
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
      <table className="w-full text-left text-sm">
        <thead className="border-b border-slate-200 bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
          <tr>
            <th className="px-4 py-3">Operation</th>
            <th className="px-4 py-3">Level</th>
            <th className="px-4 py-3">Score</th>
            <th className="px-4 py-3">Assessed at</th>
          </tr>
        </thead>
        <tbody>
          {events.map((event) => (
            <tr key={event.id} className="border-b border-slate-100 last:border-0">
              <td className="px-4 py-3 font-mono text-xs text-slate-500">
                {event.operation_id.slice(0, 8)}
              </td>
              <td className="px-4 py-3">
                <span
                  className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                    LEVEL_BADGE[event.risk_level] || "bg-slate-100 text-slate-700"
                  }`}
                >
                  {event.risk_level}
                </span>
              </td>
              <td className="px-4 py-3 tabular-nums text-slate-700">
                {event.risk_score.toFixed(3)}
              </td>
              <td className="px-4 py-3 text-slate-500">
                {new Date(event.created_at).toLocaleString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
