import { PieChart, Pie, Cell, ResponsiveContainer } from "recharts";

const LEVEL_COLORS = {
  low: "#16a34a",
  medium: "#ca8a04",
  high: "#ea580c",
  critical: "#dc2626",
};

export default function RiskGauge({ score, level }) {
  const safeScore = Math.min(Math.max(score ?? 0, 0), 1);
  const color = LEVEL_COLORS[level] || "#64748b";

  const data = [
    { name: "score", value: safeScore },
    { name: "remaining", value: 1 - safeScore },
  ];

  return (
    <div className="relative h-48">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            dataKey="value"
            cx="50%"
            cy="80%"
            startAngle={180}
            endAngle={0}
            innerRadius={70}
            outerRadius={100}
            stroke="none"
            isAnimationActive={false}
          >
            <Cell fill={color} />
            <Cell fill="#e2e8f0" />
          </Pie>
        </PieChart>
      </ResponsiveContainer>

      <div className="absolute inset-x-0 bottom-6 text-center">
        <div className="text-3xl font-semibold text-slate-800">
          {safeScore.toFixed(2)}
        </div>
        <div
          className="text-sm font-medium uppercase tracking-wide"
          style={{ color }}
        >
          {level || "unknown"}
        </div>
      </div>
    </div>
  );
}
