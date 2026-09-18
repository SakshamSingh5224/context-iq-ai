import { useCallback, useEffect, useState } from "react";
import {
  assessOperation,
  createOperation,
  listRiskEvents,
} from "./api.js";
import AssessmentCard from "./components/AssessmentCard.jsx";
import RiskEventsTable from "./components/RiskEventsTable.jsx";

const EMPTY_FORM = {
  title: "",
  description: "",
  priority: "medium",
  latitude: "",
  longitude: "",
};

export default function App() {
  const [form, setForm] = useState(EMPTY_FORM);
  const [assessment, setAssessment] = useState(null);
  const [events, setEvents] = useState([]);
  const [submitting, setSubmitting] = useState(false);
  const [eventsLoading, setEventsLoading] = useState(true);
  const [error, setError] = useState(null);

  const refreshEvents = useCallback(async () => {
    setEventsLoading(true);
    try {
      setEvents(await listRiskEvents());
    } catch (err) {
      setError(err.message);
    } finally {
      setEventsLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshEvents();
  }, [refreshEvents]);

  const updateField = (field) => (e) =>
    setForm((prev) => ({ ...prev, [field]: e.target.value }));

  const handleSubmit = async () => {
    setError(null);
    setSubmitting(true);
    setAssessment(null);

    try {
      const payload = {
        title: form.title,
        description: form.description || null,
        priority: form.priority,
      };

      if (form.latitude !== "" && form.longitude !== "") {
        payload.latitude = parseFloat(form.latitude);
        payload.longitude = parseFloat(form.longitude);
      }

      const operation = await createOperation(payload);
      const result = await assessOperation(operation.id);

      setAssessment(result);
      setForm(EMPTY_FORM);
      await refreshEvents();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const canSubmit = form.title.trim() !== "" && !submitting;

  return (
    <div className="min-h-screen bg-slate-50 px-6 py-10">
      <div className="mx-auto max-w-5xl space-y-8">
        <header>
          <h1 className="text-2xl font-semibold text-slate-900">ContextIQ AI</h1>
          <p className="text-sm text-slate-500">
            Operational risk and decision intelligence
          </p>
        </header>

        <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-sm font-medium uppercase tracking-wide text-slate-500">
            New operation
          </h2>

          <div className="grid gap-4 sm:grid-cols-2">
            <label className="sm:col-span-2">
              <span className="mb-1 block text-sm text-slate-600">Title</span>
              <input
                type="text"
                value={form.title}
                onChange={updateField("title")}
                placeholder="Inspect cold-storage unit 4"
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-slate-500"
              />
            </label>

            <label className="sm:col-span-2">
              <span className="mb-1 block text-sm text-slate-600">
                Description
              </span>
              <textarea
                value={form.description}
                onChange={updateField("description")}
                rows={2}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-slate-500"
              />
            </label>

            <label>
              <span className="mb-1 block text-sm text-slate-600">Priority</span>
              <select
                value={form.priority}
                onChange={updateField("priority")}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-slate-500"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="urgent">Urgent</option>
              </select>
            </label>

            <div className="grid grid-cols-2 gap-3">
              <label>
                <span className="mb-1 block text-sm text-slate-600">
                  Latitude
                </span>
                <input
                  type="number"
                  step="any"
                  value={form.latitude}
                  onChange={updateField("latitude")}
                  placeholder="26.8467"
                  className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-slate-500"
                />
              </label>
              <label>
                <span className="mb-1 block text-sm text-slate-600">
                  Longitude
                </span>
                <input
                  type="number"
                  step="any"
                  value={form.longitude}
                  onChange={updateField("longitude")}
                  placeholder="80.9462"
                  className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-slate-500"
                />
              </label>
            </div>
          </div>

          <button
            onClick={handleSubmit}
            disabled={!canSubmit}
            className="mt-5 inline-flex items-center gap-2 rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:bg-slate-400"
          >
            {submitting && (
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
            )}
            {submitting ? "Assessing..." : "Create & assess"}
          </button>

          {error && (
            <p className="mt-3 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
              {error}
            </p>
          )}
        </section>

        {assessment && <AssessmentCard assessment={assessment} />}

        <section>
          <h2 className="mb-3 text-sm font-medium uppercase tracking-wide text-slate-500">
            Risk history
          </h2>
          <RiskEventsTable events={events} loading={eventsLoading} />
        </section>
      </div>
    </div>
  );
}
