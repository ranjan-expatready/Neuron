"use client";

import { useEffect, useMemo, useState } from "react";

type Blocker = {
  code: string;
  message?: string;
  severity?: string;
  config_refs?: string[];
  source_refs?: string[];
  rule_refs?: string[];
};

type DocumentEntry = {
  id: string;
  label?: string;
  category?: string;
  unsourced?: boolean;
  config_refs?: string[];
  source_refs?: string[];
};

type SubmissionReadinessResult = {
  status?: string;
  ready?: boolean;
  missing_documents: string[];
  documents: DocumentEntry[];
  blockers: Blocker[];
  explanations?: string[];
  evaluation_timestamp?: string;
  engine_version?: string;
  config_hash?: string;
  source_bundle_version?: string;
};

type VerificationResult = {
  verdict: "PASS" | "FAIL" | "UNKNOWN" | string;
  reasons: string[];
  warnings: string[];
};

type EvidenceBundle = {
  bundle_version: string;
  case_id: string;
  tenant_id: string;
  program_code: string;
  engine_version: string;
  verification_engine_version: string;
  evaluation_timestamp: string;
  config_hashes: string[];
  consulted_configs?: string[];
  source_bundle_version?: string;
  readiness_result: SubmissionReadinessResult;
  verification_result: VerificationResult;
  evidence_index: string[];
};

async function fetchJson(url: string) {
  const res = await fetch(url);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Request failed (${res.status})`);
  }
  return res.json();
}

function badgeClasses(verdict: string) {
  if (verdict === "PASS") return "bg-green-100 text-green-800 border-green-200";
  if (verdict === "FAIL") return "bg-red-100 text-red-800 border-red-200";
  return "bg-amber-100 text-amber-800 border-amber-200";
}

function humanVerdict(verdict: string) {
  if (verdict === "PASS") return "PASS – ready to proceed (shadow)";
  if (verdict === "FAIL") return "FAIL – blockers remain";
  return "UNKNOWN – ambiguous or unsourced";
}

export default function SubmissionReadinessPage({ params }: { params: { caseId: string } }) {
  const { caseId } = params;
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [readiness, setReadiness] = useState<SubmissionReadinessResult | null>(null);
  const [evidence, setEvidence] = useState<EvidenceBundle | null>(null);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const [r, e] = await Promise.all([
          fetchJson(`/api/v1/cases/${caseId}/submission-readiness`),
          fetchJson(`/api/v1/cases/${caseId}/submission-readiness/evidence`),
        ]);
        setReadiness(r);
        setEvidence(e);
      } catch (err: any) {
        setError(err?.message || "Unable to load submission readiness");
      } finally {
        setLoading(false);
      }
    };
    load().catch(() => null);
  }, [caseId]);

  const docMap = useMemo(() => {
    const map = new Map<string, DocumentEntry>();
    readiness?.documents?.forEach((d) => map.set(d.id, d));
    return map;
  }, [readiness]);

  const missingDocs = useMemo(() => {
    const entries = (readiness?.missing_documents || []).map((id) => ({
      id,
      ...(docMap.get(id) || {}),
    }));
    return entries.sort((a, b) => a.id.localeCompare(b.id));
  }, [readiness, docMap]);

  const blockers = useMemo(() => {
    return [...(readiness?.blockers || [])].sort((a, b) => a.code.localeCompare(b.code));
  }, [readiness]);

  const verdict = evidence?.verification_result?.verdict || "UNKNOWN";
  const explanations = readiness?.explanations || [];

  const downloadEvidence = () => {
    if (!evidence) return;
    const blob = new Blob([JSON.stringify(evidence, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `case-${caseId}-readiness-evidence-v1.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 text-gray-900">
        <div className="mx-auto max-w-5xl px-4 py-10 space-y-4">
          <div className="h-6 w-48 animate-pulse rounded bg-gray-200" aria-label="Loading header" />
          <div className="h-32 w-full animate-pulse rounded bg-gray-200" aria-label="Loading panel" />
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

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <div className="mx-auto max-w-5xl px-4 py-8 space-y-6">
        <div className="rounded border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-900">
          <div className="font-semibold">Submission Readiness (Shadow, Read-only)</div>
          <div>RCIC / Admin / Owner only. Backend enforces RBAC; no mutations or submission actions.</div>
        </div>

        <div className="flex items-center justify-between gap-3">
          <div>
            <p className="text-xs uppercase text-gray-500">Case {caseId}</p>
            <h1 className="text-2xl font-semibold text-gray-900">Readiness & Evidence</h1>
          </div>
          <div
            className={`rounded border px-3 py-1 text-sm font-semibold ${badgeClasses(verdict)}`}
            aria-label="Readiness verification status"
          >
            {humanVerdict(verdict)}
          </div>
        </div>

        {explanations?.length > 0 && (
          <div className="rounded border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900 space-y-1">
            <div className="font-semibold">Explanations</div>
            {explanations.map((msg, idx) => (
              <div key={`exp-${idx}`}>{msg}</div>
            ))}
          </div>
        )}

        <div className="grid gap-4 lg:grid-cols-2">
          <div className="space-y-3 rounded border border-gray-200 bg-white p-4 shadow-sm">
            <div className="flex items-center justify-between">
              <h2 className="text-base font-semibold text-gray-900">What&apos;s Missing</h2>
              <span className="text-xs text-gray-500">Stable ordering</span>
            </div>
            {missingDocs.length === 0 ? (
              <div className="text-sm text-gray-600">No missing documents detected.</div>
            ) : (
              <ul className="space-y-2" aria-label="Missing documents list">
                {missingDocs.map((doc) => (
                  <li key={doc.id} className="rounded border border-gray-100 bg-gray-50 p-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-semibold text-gray-900">{doc.label || doc.id}</p>
                        <p className="text-xs text-gray-600">{doc.category || "No category"}</p>
                      </div>
                      {doc.unsourced ? (
                        <span className="rounded-full bg-amber-100 px-2 py-1 text-2xs font-semibold text-amber-800">
                          UNSOURCED
                        </span>
                      ) : (
                        <span className="rounded-full bg-red-100 px-2 py-1 text-2xs font-semibold text-red-700">
                          Missing
                        </span>
                      )}
                    </div>
                    {doc.config_refs?.length ? (
                      <div className="mt-1 text-xs text-gray-700">Config: {doc.config_refs.join(", ")}</div>
                    ) : null}
                    {doc.source_refs?.length ? (
                      <div className="mt-1 text-xs text-gray-700">Source: {doc.source_refs.join(", ")}</div>
                    ) : null}
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="space-y-3 rounded border border-gray-200 bg-white p-4 shadow-sm">
            <div className="flex items-center justify-between">
              <h2 className="text-base font-semibold text-gray-900">Blockers</h2>
              <span className="text-xs text-gray-500">Deterministic order</span>
            </div>
            {blockers.length === 0 ? (
              <div className="text-sm text-gray-600">No blockers reported.</div>
            ) : (
              <ul className="space-y-2" aria-label="Blockers list">
                {blockers.map((blk) => (
                  <li key={blk.code} className="rounded border border-gray-100 bg-gray-50 p-3">
                    <div className="flex items-center justify-between">
                      <div className="text-sm font-semibold text-gray-900">{blk.code}</div>
                      {blk.severity && (
                        <span className="rounded-full bg-gray-200 px-2 py-1 text-2xs font-semibold text-gray-800">
                          {blk.severity}
                        </span>
                      )}
                    </div>
                    {blk.message && <div className="text-sm text-gray-700">{blk.message}</div>}
                    {blk.rule_refs?.length ? (
                      <div className="text-xs text-gray-600 mt-1">Rules: {blk.rule_refs.join(", ")}</div>
                    ) : null}
                    {blk.config_refs?.length ? (
                      <div className="text-xs text-gray-600 mt-1">Config: {blk.config_refs.join(", ")}</div>
                    ) : null}
                    {blk.source_refs?.length ? (
                      <div className="text-xs text-gray-600 mt-1">Source: {blk.source_refs.join(", ")}</div>
                    ) : null}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        <div className="space-y-3 rounded border border-gray-200 bg-white p-4 shadow-sm">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <div>
              <h2 className="text-base font-semibold text-gray-900">Evidence & Audit</h2>
              <p className="text-xs text-gray-600">Deterministic bundle v1; read-only export.</p>
            </div>
            <button
              onClick={downloadEvidence}
              className="rounded bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-60"
              disabled={!evidence}
            >
              Download Evidence (JSON)
            </button>
          </div>

          <div className="grid gap-3 md:grid-cols-2">
            <div className="rounded border border-gray-100 bg-gray-50 p-3 text-sm">
              <div className="font-semibold text-gray-900">Engine versions</div>
              <div className="text-gray-700">Readiness: {evidence?.engine_version || readiness?.engine_version || "—"}</div>
              <div className="text-gray-700">
                Verification: {evidence?.verification_engine_version || "—"}
              </div>
            </div>
            <div className="rounded border border-gray-100 bg-gray-50 p-3 text-sm">
              <div className="font-semibold text-gray-900">Timestamps & Hashes</div>
              <div className="text-gray-700">Evaluated: {evidence?.evaluation_timestamp || readiness?.evaluation_timestamp || "—"}</div>
              <div className="text-gray-700">
                Config hashes: {evidence?.config_hashes?.join(", ") || readiness?.config_hash || "—"}
              </div>
              <div className="text-gray-700">
                Source bundle: {evidence?.source_bundle_version || readiness?.source_bundle_version || "—"}
              </div>
            </div>
          </div>

          {evidence?.evidence_index?.length ? (
            <div className="space-y-2">
              <div className="font-semibold text-sm text-gray-900">Evidence index</div>
              <ul className="space-y-1" aria-label="Evidence index list">
                {evidence.evidence_index.map((ref) => {
                  const isUrl = /^https?:\/\//i.test(ref);
                  return (
                    <li key={ref} className="text-sm text-gray-700">
                      {isUrl ? (
                        <a className="text-indigo-700 underline" href={ref} target="_blank" rel="noreferrer">
                          {ref}
                        </a>
                      ) : (
                        <code className="rounded bg-gray-100 px-2 py-1 text-xs text-gray-800">{ref}</code>
                      )}
                    </li>
                  );
                })}
              </ul>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}

