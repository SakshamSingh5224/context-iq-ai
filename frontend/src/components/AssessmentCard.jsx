import RiskGauge from "./RiskGauge.jsx";

const FACTOR_LABELS = {
  internal: "Internal",
  external: "External",
  time_pressure: "Time pressure",
  historical: "Historical",
};

export default function AssessmentCard({ assessment }) {
  if (!assessment) return null;

  const { title, risk_assessment: risk, copilot_strategy: strategy } = assessment;
  const breakdown = risk?.breakdown || {};
  const maxWeighted = Math.max(...Object.values(breakdown), 0.0001);

  return (
    <div className="grid gap-6 md:grid-cols-2">
      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="mb-1 text-sm font-medium uppercase tracking-wide text-slate-500">
          Risk assessment
        </h2>
        <p className="mb-4 text-lg font-semibold text-slate-800">{title}</p>

        <RiskGauge score={risk?.score} level={risk?.level} />

        <div className="mt-4 space-y-2">
          {Object.entries(breakdown).map(([key, value]) => (
            <div key={key}>
              <div className="flex justify-between text-sm text-slate-600">
                <span>{FACTOR_LABELS[key] || key}</span>
                <span className="tabular-nums">{value.toFixed(3)}</span>
              </div>
              <div className="h-1.5 rounded-full bg-slate-100">
                <div
                  className="h-1.5 rounded-full bg-slate-400"
                  style={{ width: `${(value / maxWeighted) * 100}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="mb-3 text-sm font-medium uppercase tracking-wide text-slate-500">
          Copilot strategy
        </h2>
        <pre className="whitespace-pre-wrap break-words font-sans text-sm leading-relaxed text-slate-700">
          {strategy}
        </pre>
      </section>
    </div>
  );
}
