"use client";

import { useEffect, useMemo, useState } from "react";

type Draft = {
  id: string;
  config_type: string;
  key: string;
  status: string;
  created_by: string;
  updated_by: string;
  created_at: string;
  updated_at: string;
  payload: any;
  notes?: string | null;
};

const panelClass = "border rounded-md border-gray-200 bg-white shadow-sm";

export default function AdminIntakeDraftsPage() {
  const [drafts, setDrafts] = useState<Draft[]>([]);
  const [selected, setSelected] = useState<Draft | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filterType, setFilterType] = useState<string>("");
  const [filterStatus, setFilterStatus] = useState<string>("");

  const loadDrafts = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (filterType) params.set("config_type", filterType);
      if (filterStatus) params.set("status", filterStatus);
      const res = await fetch(`/api/v1/admin/intake/drafts?${params.toString()}`);
      if (!res.ok) throw new Error(`Failed to load drafts (${res.status})`);
      const data = await res.json();
      setDrafts(data);
      setSelected((prev) => (prev ? data.find((d: Draft) => d.id === prev.id) || null : null));
    } catch (err) {
      console.error(err);
      setError("Unable to load drafts. Check permissions or backend status.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadDrafts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filterType, filterStatus]);

  const [formPayload, setFormPayload] = useState<string>("{}");
  const [formType, setFormType] = useState<string>("field");
  const [formKey, setFormKey] = useState<string>("");
  const [formError, setFormError] = useState<string | null>(null);
  const [formSaving, setFormSaving] = useState(false);

  const handleCreate = async () => {
    setFormError(null);
    setFormSaving(true);
    try {
      const parsed = JSON.parse(formPayload || "{}");
      const res = await fetch("/api/v1/admin/intake/drafts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ config_type: formType, key: formKey || parsed.id || "", payload: parsed }),
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `Create failed (${res.status})`);
      }
      setFormPayload("{}");
      setFormKey("");
      await loadDrafts();
    } catch (err: any) {
      setFormError(err.message || "Create failed");
    } finally {
      setFormSaving(false);
    }
  };

  const filteredDrafts = useMemo(() => drafts, [drafts]);

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <div className="mx-auto max-w-6xl px-4 py-8 space-y-4">
        <div className="rounded-md border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-900">
          <div className="font-semibold">Intake Config Drafts (Read-only runtime)</div>
          <div>
            Drafts are proposals only. Runtime intake/document engine still reads YAML in config/domain; activation will
            come in M7.3.
          </div>
        </div>

        <div className="flex gap-3">
          <div>
            <label className="text-xs font-semibold text-gray-700">Config type</label>
            <select
              className="mt-1 block rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm"
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
            >
              <option value="">All</option>
              <option value="field">Field</option>
              <option value="template">Template</option>
              <option value="document">Document</option>
              <option value="form">Form</option>
            </select>
          </div>
          <div>
            <label className="text-xs font-semibold text-gray-700">Status</label>
            <select
              className="mt-1 block rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm"
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
            >
              <option value="">All</option>
              <option value="draft">Draft</option>
              <option value="in_review">In review</option>
              <option value="rejected">Rejected</option>
            </select>
          </div>
          <div className="flex items-end">
            <button
              onClick={loadDrafts}
              className="rounded-md bg-gray-200 px-3 py-2 text-sm font-medium text-gray-800 hover:bg-gray-300"
            >
              Refresh
            </button>
          </div>
        </div>

        {error && <div className="rounded-md border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700">{error}</div>}
        {loading && <div className="text-sm text-gray-600">Loading drafts…</div>}

        <div className="grid grid-cols-12 gap-4">
          <div className="col-span-12 md:col-span-6">
            <div className={panelClass}>
              <div className="border-b px-4 py-3 font-semibold">Drafts</div>
              <div className="max-h-[70vh] overflow-y-auto divide-y">
                {filteredDrafts.length === 0 ? (
                  <div className="px-4 py-3 text-sm text-gray-600">No drafts found.</div>
                ) : (
                  filteredDrafts.map((d) => (
                    <button
                      key={d.id}
                      className={`w-full text-left px-4 py-3 text-sm hover:bg-gray-100 ${
                        selected?.id === d.id ? "bg-blue-50" : ""
                      }`}
                      onClick={() => setSelected(d)}
                    >
                      <div className="flex items-center justify-between">
                        <div className="font-semibold text-gray-900">{d.key}</div>
                        <span className="rounded-md bg-gray-100 px-2 py-1 text-2xs text-gray-700">{d.config_type}</span>
                      </div>
                      <div className="text-xs text-gray-600">
                        Status: {d.status} • Updated: {new Date(d.updated_at).toLocaleString()}
                      </div>
                    </button>
                  ))
                )}
              </div>
            </div>
          </div>

          <div className="col-span-12 md:col-span-6 space-y-4">
            <div className={panelClass}>
              <div className="border-b px-4 py-3 font-semibold">Create Draft</div>
              <div className="space-y-2 p-4 text-sm">
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-xs font-semibold text-gray-700">Config type</label>
                    <select
                      className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm"
                      value={formType}
                      onChange={(e) => setFormType(e.target.value)}
                    >
                      <option value="field">Field</option>
                      <option value="template">Template</option>
                      <option value="document">Document</option>
                      <option value="form">Form</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-xs font-semibold text-gray-700">Key (id)</label>
                    <input
                      className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm"
                      value={formKey}
                      onChange={(e) => setFormKey(e.target.value)}
                      placeholder="e.g., person.test_field"
                    />
                  </div>
                </div>
                <div>
                  <label htmlFor="payload-json" className="text-xs font-semibold text-gray-700">
                    Payload (JSON)
                  </label>
                  <textarea
                    id="payload-json"
                    className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm font-mono"
                    rows={8}
                    value={formPayload}
                    onChange={(e) => setFormPayload(e.target.value)}
                  />
                </div>
                {formError && <div className="text-xs text-red-700">{formError}</div>}
                <button
                  onClick={handleCreate}
                  disabled={formSaving}
                  className="rounded-md bg-blue-600 px-3 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
                >
                  {formSaving ? "Saving..." : "Save Draft"}
                </button>
              </div>
            </div>

            <div className={panelClass}>
              <div className="border-b px-4 py-3 font-semibold">Details</div>
              <div className="p-4 text-sm">
                {selected ? (
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="font-semibold">{selected.key}</div>
                      <span className="rounded-md bg-gray-100 px-2 py-1 text-2xs text-gray-700">
                        {selected.config_type}
                      </span>
                    </div>
                    <div className="text-xs text-gray-600">
                      Status: {selected.status} • Updated: {new Date(selected.updated_at).toLocaleString()}
                    </div>
                    <pre className="mt-2 max-h-64 overflow-auto rounded-md bg-gray-100 p-3 text-xs">
{JSON.stringify(selected.payload, null, 2)}
                    </pre>
                  </div>
                ) : (
                  <div className="text-gray-600">Select a draft to view details.</div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

