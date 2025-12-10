"use client";

import { useEffect, useMemo, useState } from "react";

type AgentAction = {
  id: string;
  agent_name: string;
  action_type: string;
  status: string;
  case_id?: string | null;
  created_at: string;
  payload?: any;
};

const panelClass = "border rounded-md border-gray-200 bg-white shadow-sm";

export default function AdminAgentsPage() {
  const [actions, setActions] = useState<AgentAction[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [agentFilter, setAgentFilter] = useState("");
  const [caseFilter, setCaseFilter] = useState("");
  const [selected, setSelected] = useState<AgentAction | null>(null);
  const [settings, setSettings] = useState({
    auto_intake_reminders_enabled: false,
    auto_missing_docs_reminders_enabled: false,
    min_days_between_intake_reminders: 7,
    min_days_between_docs_reminders: 7,
  });
  const [savingSettings, setSavingSettings] = useState(false);
  const [autoRunSummary, setAutoRunSummary] = useState<string | null>(null);

  const loadActions = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (agentFilter) params.set("agent_name", agentFilter);
      if (caseFilter) params.set("case_id", caseFilter);
      const res = await fetch(`/api/v1/admin/agents/actions?${params.toString()}`);
      if (!res.ok) throw new Error(`Failed to load actions (${res.status})`);
      const data = await res.json();
      setActions(data);
      setSelected((prev) => (prev ? data.find((a: AgentAction) => a.id === prev.id) || null : null));
    } catch (err: any) {
      setError(err.message || "Failed to load agent actions");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadActions();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [agentFilter, caseFilter]);

  const loadSettings = async () => {
    try {
      const res = await fetch("/api/v1/admin/agents/client-engagement/settings");
      if (!res.ok) throw new Error(`Failed to load settings (${res.status})`);
      const data = await res.json();
      setSettings(data);
    } catch (err: any) {
      setError(err.message || "Failed to load settings");
    }
  };

  useEffect(() => {
    void loadSettings();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const saveSettings = async () => {
    setSavingSettings(true);
    setError(null);
    try {
      const res = await fetch("/api/v1/admin/agents/client-engagement/settings", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(settings),
      });
      if (!res.ok) throw new Error(`Failed to save settings (${res.status})`);
      const data = await res.json();
      setSettings(data);
    } catch (err: any) {
      setError(err.message || "Failed to save settings");
    } finally {
      setSavingSettings(false);
    }
  };

  const runAutoTenant = async () => {
    setAutoRunSummary(null);
    setError(null);
    try {
      const res = await fetch("/api/v1/admin/agents/client-engagement/auto-run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scope: "tenant" }),
      });
      if (!res.ok) throw new Error(`Auto-run failed (${res.status})`);
      const data = await res.json();
      setAutoRunSummary(
        `Processed ${data.cases_processed} cases; intake reminders ${data.intake_reminders}, docs reminders ${data.docs_reminders}`
      );
    } catch (err: any) {
      setError(err.message || "Failed to run auto mode");
    }
  };

  const filtered = useMemo(() => actions, [actions]);

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <div className="mx-auto max-w-6xl px-4 py-8 space-y-4">
        <div className="rounded-md border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-900">
          <div className="font-semibold">Agent Activity (M8.0 skeleton)</div>
          <div>View-only audit of agent suggestions. No auto-sends; suggestions only.</div>
        </div>

        <div className="rounded-md border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-900 space-y-2">
          <div className="font-semibold">Client Engagement AUTO Settings (intake/docs only)</div>
          <div className="grid gap-3 md:grid-cols-4">
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={settings.auto_intake_reminders_enabled}
                onChange={(e) => setSettings((s) => ({ ...s, auto_intake_reminders_enabled: e.target.checked }))}
              />
              Enable AUTO intake reminders
            </label>
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={settings.auto_missing_docs_reminders_enabled}
                onChange={(e) => setSettings((s) => ({ ...s, auto_missing_docs_reminders_enabled: e.target.checked }))}
              />
              Enable AUTO missing-docs reminders
            </label>
            <div className="text-sm">
              <div className="text-xs text-gray-700">Min days between intake reminders</div>
              <input
                type="number"
                min={1}
                max={30}
                value={settings.min_days_between_intake_reminders}
                onChange={(e) => setSettings((s) => ({ ...s, min_days_between_intake_reminders: Number(e.target.value) }))}
                className="mt-1 block w-full rounded-md border border-gray-300 px-2 py-1 text-sm"
              />
            </div>
            <div className="text-sm">
              <div className="text-xs text-gray-700">Min days between docs reminders</div>
              <input
                type="number"
                min={1}
                max={30}
                value={settings.min_days_between_docs_reminders}
                onChange={(e) => setSettings((s) => ({ ...s, min_days_between_docs_reminders: Number(e.target.value) }))}
                className="mt-1 block w-full rounded-md border border-gray-300 px-2 py-1 text-sm"
              />
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={saveSettings}
              className="rounded-md bg-indigo-600 px-3 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-60"
              disabled={savingSettings}
            >
              {savingSettings ? "Saving…" : "Save settings"}
            </button>
            <button
              onClick={runAutoTenant}
              className="rounded-md bg-gray-200 px-3 py-2 text-sm font-medium text-gray-800 hover:bg-gray-300"
            >
              Run AUTO for this tenant now
            </button>
            {autoRunSummary && <span className="text-xs text-gray-700">{autoRunSummary}</span>}
          </div>
          <div className="text-xs text-gray-700">
            AUTO applies only to intake/doc reminders. Client question replies remain shadow-only; no cron is scheduled in-app.
          </div>
        </div>

        <div className="flex gap-3 flex-wrap">
          <div>
            <label className="text-xs font-semibold text-gray-700">Agent</label>
            <input
              className="mt-1 block rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm"
              value={agentFilter}
              onChange={(e) => setAgentFilter(e.target.value)}
              placeholder="e.g., client_engagement"
            />
          </div>
          <div>
            <label className="text-xs font-semibold text-gray-700">Case ID</label>
            <input
              className="mt-1 block rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm"
              value={caseFilter}
              onChange={(e) => setCaseFilter(e.target.value)}
              placeholder="optional"
            />
          </div>
          <div className="flex items-end">
            <button
              onClick={loadActions}
              className="rounded-md bg-gray-200 px-3 py-2 text-sm font-medium text-gray-800 hover:bg-gray-300"
            >
              Refresh
            </button>
          </div>
        </div>

        {error && <div className="rounded-md border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700">{error}</div>}
        {loading && <div className="text-sm text-gray-600">Loading actions…</div>}

        <div className="grid grid-cols-12 gap-4">
          <div className="col-span-12 md:col-span-7">
            <div className={panelClass}>
              <div className="border-b px-4 py-3 font-semibold">Actions</div>
              <div className="max-h-[70vh] overflow-y-auto divide-y">
                {filtered.length === 0 ? (
                  <div className="px-4 py-3 text-sm text-gray-600">No actions found.</div>
                ) : (
                  filtered.map((a) => (
                    <button
                      key={a.id}
                      className={`w-full text-left px-4 py-3 text-sm hover:bg-gray-100 ${
                        selected?.id === a.id ? "bg-blue-50" : ""
                      }`}
                      onClick={() => setSelected(a)}
                    >
                      <div className="flex items-center justify-between">
                        <div className="font-semibold text-gray-900">{a.agent_name}</div>
                        <span className="rounded-md bg-gray-100 px-2 py-1 text-2xs text-gray-700">{a.status}</span>
                      </div>
                      <div className="text-xs text-gray-600">
                        {a.action_type} • Case: {a.case_id || "n/a"} • {new Date(a.created_at).toLocaleString()}
                      </div>
                    </button>
                  ))
                )}
              </div>
            </div>
          </div>

          <div className="col-span-12 md:col-span-5">
            <div className={panelClass}>
              <div className="border-b px-4 py-3 font-semibold">Details</div>
              <div className="p-4 text-sm">
                {selected ? (
                  <div className="space-y-2">
                    <div className="font-semibold">{selected.agent_name}</div>
                    <div className="text-xs text-gray-600">
                      {selected.action_type} • Case: {selected.case_id || "n/a"} • {selected.status}
                    </div>
                    <pre className="max-h-64 overflow-auto rounded-md bg-gray-100 p-3 text-xs">
{JSON.stringify(selected.payload || {}, null, 2)}
                    </pre>
                  </div>
                ) : (
                  <div className="text-gray-600">Select an action to view details.</div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

