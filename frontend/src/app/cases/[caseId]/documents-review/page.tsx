"use client";

import { useEffect, useState } from "react";

type Findings = {
  required_present: any[];
  required_missing: any[];
  optional_present: any[];
  duplicates: any[];
  unmatched: any[];
  content_warnings?: any[];
  quality_warnings?: any[];
  heuristic_findings?: any[];
};

type ReviewResponse = {
  program_code: string;
  case_id: string;
  findings: Findings;
  agent_action_id: string;
  agent_session_id: string;
};

async function runReview(caseId: string): Promise<ReviewResponse> {
  const res = await fetch("/api/v1/admin/agents/document-review", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ case_id: caseId }),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Failed to run review (${res.status}): ${text}`);
  }
  return res.json();
}

export default function DocumentsReviewPage({ params }: { params: { caseId: string } }) {
  const { caseId } = params;
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ReviewResponse | null>(null);

  const fetchLatest = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await runReview(caseId);
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Failed to run document review");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLatest().catch(() => null);
  }, [caseId]);

  const list = (title: string, items: any[]) => (
    <div className="space-y-1">
      <div className="font-semibold text-sm">{title}</div>
      {(!items || items.length === 0) && <div className="text-xs text-gray-500">None</div>}
      {items?.map((item, idx) => (
        <div key={`${title}-${idx}`} className="rounded border border-gray-200 bg-gray-50 p-2 text-xs">
          {item.finding_code || item.label || item.document_type || item.requirement_id || item.issue || "entry"}
          {item.severity && <span className="ml-1 text-gray-600">({item.severity})</span>}
          {item.filenames && item.filenames.length > 0 && (
            <div className="text-gray-600">Files: {item.filenames.join(", ")}</div>
          )}
          {item.issue && (
            <div className="text-gray-600">
              Issue: {item.issue}
              {item.extension ? ` (${item.extension})` : ""}
            </div>
          )}
          {item.details && (
            <div className="text-gray-600">
              Details: {typeof item.details === "string" ? item.details : JSON.stringify(item.details)}
            </div>
          )}
        </div>
      ))}
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <div className="mx-auto max-w-4xl px-4 py-8 space-y-4">
        <div className="rounded border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-900">
          <div className="font-semibold">Document Reviewer Agent (Shadow)</div>
          <div>AI-assisted suggestions only. RCIC must review and take action. No auto-send or lifecycle changes.</div>
        </div>

        {error && <div className="rounded border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700">{error}</div>}

        <button
          className="rounded bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-60"
          onClick={fetchLatest}
          disabled={loading}
        >
          {loading ? "Running review…" : "Run Document Review"}
        </button>

        {result && (
          <div className="rounded border border-gray-200 bg-white p-4 shadow-sm space-y-3">
            <div className="text-sm text-gray-700">
              Program: <span className="font-semibold">{result.program_code}</span>
            </div>
            <div className="grid gap-3 md:grid-cols-2">
              {list("Required present", result.findings.required_present)}
              {list("Required missing", result.findings.required_missing)}
              {list("Optional present", result.findings.optional_present)}
              {list("Duplicates", result.findings.duplicates)}
              {list("Unmatched uploads", result.findings.unmatched)}
              {list("Content Warnings", result.findings.content_warnings || [])}
              {list("Quality Warnings", result.findings.quality_warnings || [])}
              {list("Heuristic Findings (Shadow)", result.findings.heuristic_findings || [])}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

