"use client";

import { useEffect, useMemo, useState } from "react";

type PreparationField = {
  field_code: string;
  source: string;
  value_preview: any;
  status: string;
  notes?: string | null;
};

type PreparationAttachment = {
  doc_code: string;
  status: string;
  evidence_ref?: string | null;
};

type PreparationForm = {
  form_code: string;
  form_name?: string | null;
  fields: PreparationField[];
  attachments: PreparationAttachment[];
};

type GapsSummary = {
  blocking: string[];
  non_blocking: string[];
};

type SubmissionPreparationPackage = {
  package_version: string;
  case_id: string;
  tenant_id: string;
  program_code: string;
  engine_versions: string[];
  evaluation_timestamp: string;
  forms: PreparationForm[];
  gaps_summary: GapsSummary;
  readiness_reference: {
    readiness_verdict: string;
    evidence_bundle_ref?: string | null;
  };
  audit: {
    config_hashes?: string[];
    consulted_configs?: string[];
    source_bundle_version?: string | null;
  };
  deterministic_hash: string;
};

export default function SubmissionPreparationPage({ params }: { params: { caseId: string } }) {
  const { caseId } = params;
  const [pkg, setPkg] = useState<SubmissionPreparationPackage | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`/api/v1/cases/${caseId}/submission-preparation`);
        if (!res.ok) {
          const text = await res.text();
          throw new Error(text || `Failed to load submission preparation (${res.status})`);
        }
        const data = (await res.json()) as SubmissionPreparationPackage;
        setPkg(data);
      } catch (err: any) {
        setError(err?.message || "Unable to load submission preparation package");
      } finally {
        setLoading(false);
      }
    };
    load().catch(() => null);
  }, [caseId]);

  const blockingCount = pkg?.gaps_summary.blocking.length || 0;
  const nonBlockingCount = pkg?.gaps_summary.non_blocking.length || 0;

  const attachmentsGrouped = useMemo(() => {
    const available: PreparationAttachment[] = [];
    const missing: PreparationAttachment[] = [];
    (pkg?.forms || []).forEach((f) => {
      f.attachments.forEach((att) => {
        if (att.status === "missing") missing.push(att);
        else available.push(att);
      });
    });
    return { available, missing };
  }, [pkg]);

  const verdict = pkg?.readiness_reference?.readiness_verdict || "UNKNOWN";

  const downloadJson = () => {
    if (!pkg) return;
    const blob = new Blob([JSON.stringify(pkg, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `case-${caseId}-submission-prep-v1.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 text-gray-900">
        <div className="mx-auto max-w-5xl px-4 py-10 space-y-4">
          <div className="h-6 w-56 animate-pulse rounded bg-gray-200" aria-label="Loading header" />
          <div className="h-24 w-full animate-pulse rounded bg-gray-200" aria-label="Loading summary" />
          <div className="h-40 w-full animate-pulse rounded bg-gray-200" aria-label="Loading panel" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 text-gray-900">
        <div className="mx-auto max-w-3xl px-4 py-10">
          <div className="rounded border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800" role="alert">
            {error}
          </div>
        </div>
      </div>
    );
  }

  if (!pkg) {
    return (
      <div className="min-h-screen bg-gray-50 text-gray-900">
        <div className="mx-auto max-w-3xl px-4 py-10">
          <div className="rounded border border-yellow-200 bg-yellow-50 px-4 py-3 text-sm text-yellow-800">
            No submission preparation package available.
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <div className="mx-auto max-w-5xl px-4 py-8 space-y-6">
        <div className="rounded border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-900">
          <div className="font-semibold">Submission Preparation Package (Shadow, Read-only)</div>
          <div>RCIC / Admin / Owner only. No submissions or mutations are performed.</div>
        </div>

        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-xs uppercase text-gray-500">Case {caseId}</p>
            <h1 className="text-2xl font-semibold text-gray-900">Submission Preparation</h1>
            <p className="text-sm text-gray-600">
              Program: {pkg.program_code} · Evaluated: {pkg.evaluation_timestamp}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span
              className="rounded border border-gray-300 bg-white px-3 py-1 text-xs font-semibold text-gray-800"
              aria-label="Deterministic hash"
            >
              Hash: {pkg.deterministic_hash}
            </span>
            <span
              className={`rounded px-3 py-1 text-sm font-semibold ${
                blockingCount > 0 ? "bg-red-100 text-red-800 border border-red-200" : "bg-green-100 text-green-800 border border-green-200"
              }`}
              aria-label="Blocking gaps badge"
            >
              Blocking gaps: {blockingCount}
            </span>
            <button
              onClick={downloadJson}
              className="rounded bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-60"
              aria-label="Download preparation package JSON"
            >
              Download JSON
            </button>
          </div>
        </div>

        <div className="grid gap-4 lg:grid-cols-2">
          <div className="rounded border border-red-200 bg-red-50 p-4">
            <div className="flex items-center justify-between">
              <h2 className="text-base font-semibold text-red-800">Blocking Gaps</h2>
              <span className="text-xs text-red-700">{blockingCount}</span>
            </div>
            {blockingCount === 0 ? (
              <div className="text-sm text-red-700">No blocking gaps.</div>
            ) : (
              <ul className="mt-2 space-y-1" aria-label="Blocking gaps list">
                {pkg.gaps_summary.blocking.map((g) => (
                  <li key={g} className="rounded bg-white px-2 py-1 text-sm text-red-800 border border-red-100">
                    {g}
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="rounded border border-amber-200 bg-amber-50 p-4">
            <div className="flex items-center justify-between">
              <h2 className="text-base font-semibold text-amber-800">Non-blocking Gaps</h2>
              <span className="text-xs text-amber-700">{nonBlockingCount}</span>
            </div>
            {nonBlockingCount === 0 ? (
              <div className="text-sm text-amber-800">No non-blocking gaps.</div>
            ) : (
              <ul className="mt-2 space-y-1" aria-label="Non-blocking gaps list">
                {pkg.gaps_summary.non_blocking.map((g) => (
                  <li key={g} className="rounded bg-white px-2 py-1 text-sm text-amber-800 border border-amber-100">
                    {g}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        <div className="space-y-3 rounded border border-gray-200 bg-white p-4 shadow-sm">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <div>
              <h2 className="text-base font-semibold text-gray-900">Forms</h2>
              <p className="text-xs text-gray-600">Field mapping status; stable order as returned.</p>
            </div>
          </div>

          {(pkg.forms || []).length === 0 ? (
            <div className="text-sm text-gray-600">No forms in this package.</div>
          ) : (
            <div className="space-y-4">
              {pkg.forms.map((form) => (
                <div key={form.form_code} className="rounded border border-gray-100 bg-gray-50 p-3 space-y-2">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-sm font-semibold text-gray-900">{form.form_code}</div>
                      {form.form_name && <div className="text-xs text-gray-600">{form.form_name}</div>}
                    </div>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="min-w-full text-left text-sm" aria-label={`Fields for ${form.form_code}`}>
                      <thead className="text-xs uppercase text-gray-600">
                        <tr>
                          <th className="px-2 py-1">Field</th>
                          <th className="px-2 py-1">Status</th>
                          <th className="px-2 py-1">Value</th>
                          <th className="px-2 py-1">Source</th>
                          <th className="px-2 py-1">Notes</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200">
                        {form.fields.map((field) => (
                          <tr key={field.field_code}>
                            <td className="px-2 py-1 font-mono text-xs text-gray-900">{field.field_code}</td>
                            <td className="px-2 py-1">
                              <span
                                className={`rounded-full px-2 py-0.5 text-2xs font-semibold ${
                                  field.status === "missing"
                                    ? "bg-red-100 text-red-800"
                                    : "bg-green-100 text-green-800"
                                }`}
                                aria-label={`Field status ${field.status}`}
                              >
                                {field.status}
                              </span>
                            </td>
                            <td className="px-2 py-1 text-gray-800 break-all">
                              {field.value_preview === null || field.value_preview === undefined
                                ? "—"
                                : typeof field.value_preview === "object"
                                ? JSON.stringify(field.value_preview)
                                : String(field.value_preview)}
                            </td>
                            <td className="px-2 py-1 text-xs text-gray-700">{field.source}</td>
                            <td className="px-2 py-1 text-xs text-gray-600">{field.notes || "—"}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="space-y-3 rounded border border-gray-200 bg-white p-4 shadow-sm">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <div>
              <h2 className="text-base font-semibold text-gray-900">Attachments</h2>
              <p className="text-xs text-gray-600">Available vs missing; evidence references shown when present.</p>
            </div>
          </div>
          <div className="grid gap-3 md:grid-cols-2">
            <div className="rounded border border-green-200 bg-green-50 p-3">
              <div className="text-sm font-semibold text-green-800">Available</div>
              {attachmentsGrouped.available.length === 0 ? (
                <div className="text-sm text-green-800">None</div>
              ) : (
                <ul className="mt-2 space-y-1" aria-label="Available attachments list">
                  {attachmentsGrouped.available.map((att) => (
                    <li key={`av-${att.doc_code}`} className="rounded bg-white px-2 py-1 text-sm text-gray-800 border border-green-100">
                      <div className="font-mono text-xs text-gray-900">{att.doc_code}</div>
                      {att.evidence_ref && <div className="text-xs text-gray-700">Ref: {att.evidence_ref}</div>}
                    </li>
                  ))}
                </ul>
              )}
            </div>
            <div className="rounded border border-red-200 bg-red-50 p-3">
              <div className="text-sm font-semibold text-red-800">Missing</div>
              {attachmentsGrouped.missing.length === 0 ? (
                <div className="text-sm text-red-800">None</div>
              ) : (
                <ul className="mt-2 space-y-1" aria-label="Missing attachments list">
                  {attachmentsGrouped.missing.map((att) => (
                    <li key={`miss-${att.doc_code}`} className="rounded bg-white px-2 py-1 text-sm text-gray-800 border border-red-100">
                      <div className="font-mono text-xs text-gray-900">{att.doc_code}</div>
                      {att.evidence_ref && <div className="text-xs text-gray-700">Ref: {att.evidence_ref}</div>}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </div>

        <div className="space-y-3 rounded border border-gray-200 bg-white p-4 shadow-sm">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div>
              <h2 className="text-base font-semibold text-gray-900">Audit & Evidence</h2>
              <p className="text-xs text-gray-600">Engine versions, configs, and readiness reference.</p>
            </div>
          </div>
          <div className="grid gap-3 md:grid-cols-2">
            <div className="rounded border border-gray-100 bg-gray-50 p-3 text-sm">
              <div className="font-semibold text-gray-900">Engine versions</div>
              <div className="text-gray-700">{(pkg.engine_versions || []).join(", ") || "—"}</div>
              <div className="text-gray-700 mt-2">
                Readiness verdict: <span className="font-semibold">{verdict}</span>
              </div>
              <div className="text-gray-700">Evidence ref: {pkg.readiness_reference?.evidence_bundle_ref || "—"}</div>
            </div>
            <div className="rounded border border-gray-100 bg-gray-50 p-3 text-sm">
              <div className="font-semibold text-gray-900">Configs & Sources</div>
              <div className="text-gray-700">Config hashes: {(pkg.audit.config_hashes || []).join(", ") || "—"}</div>
              <div className="text-gray-700">Consulted configs: {(pkg.audit.consulted_configs || []).join(", ") || "—"}</div>
              <div className="text-gray-700">
                Source bundle: {pkg.audit.source_bundle_version || "—"}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

