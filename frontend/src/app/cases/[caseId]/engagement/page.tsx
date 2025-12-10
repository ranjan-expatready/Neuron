"use client";

import { useState } from "react";

type SuggestionResponse = {
  suggestion: {
    message_type: string;
    subject?: string;
    body?: string;
    missing_sections?: string[];
    missing_documents?: string[];
    risk_level?: string;
    requires_approval?: boolean;
    llm_used?: boolean;
  };
  action_id: string;
};

async function postSuggestion(url: string, body: any): Promise<SuggestionResponse> {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Request failed (${res.status}): ${text}`);
  }
  return res.json();
}

export default function CaseEngagementPage({ params }: { params: { caseId: string } }) {
  const { caseId } = params;
  const [questionText, setQuestionText] = useState("");
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<SuggestionResponse | null>(null);

  const trigger = async (kind: "intake" | "docs" | "question") => {
    setLoading(kind);
    setError(null);
    try {
      if (kind === "intake") {
        const data = await postSuggestion(
          "/api/v1/admin/agents/client-engagement/intake-reminder",
          { case_id: caseId }
        );
        setResult(data);
      } else if (kind === "docs") {
        const data = await postSuggestion(
          "/api/v1/admin/agents/client-engagement/missing-docs-reminder",
          { case_id: caseId }
        );
        setResult(data);
      } else {
        if (!questionText.trim()) {
          setError("Please enter a client question to draft a reply.");
          setLoading(null);
          return;
        }
        const data = await postSuggestion(
          "/api/v1/admin/agents/client-engagement/client-question-reply",
          { case_id: caseId, question_text: questionText }
        );
        setResult(data);
      }
    } catch (err: any) {
      setError(err.message || "Failed to generate suggestion");
    } finally {
      setLoading(null);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <div className="mx-auto max-w-5xl px-4 py-8 space-y-6">
        <div className="rounded-md border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-900">
          <div className="font-semibold">Client Engagement (Shadow Suggestions)</div>
          <div>Template-based drafts only. RCIC must review and send; no auto-sends in M8.2.</div>
        </div>

        {error && <div className="rounded-md border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700">{error}</div>}

        <div className="grid gap-4 md:grid-cols-2">
          <div className="rounded-md border border-gray-200 bg-white shadow-sm p-4 space-y-3">
            <div className="font-semibold">Generate drafts</div>
            <button
              className="w-full rounded-md bg-indigo-600 px-3 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-60"
              disabled={loading === "intake"}
              onClick={() => trigger("intake")}
            >
              {loading === "intake" ? "Generating…" : "Intake incomplete reminder"}
            </button>
            <button
              className="w-full rounded-md bg-indigo-600 px-3 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-60"
              disabled={loading === "docs"}
              onClick={() => trigger("docs")}
            >
              {loading === "docs" ? "Generating…" : "Missing documents reminder"}
            </button>
            <div className="space-y-2">
              <label className="text-xs font-semibold text-gray-700">Client question (for draft reply)</label>
              <textarea
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm"
                rows={3}
                value={questionText}
                onChange={(e) => setQuestionText(e.target.value)}
                placeholder="Paste or type the client question"
              />
              <button
                className="w-full rounded-md bg-indigo-600 px-3 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-60"
                disabled={loading === "question"}
                onClick={() => trigger("question")}
              >
                {loading === "question" ? "Generating…" : "Draft reply to client question"}
              </button>
            </div>
            <div className="text-xs text-gray-600">
              Drafts are logged as suggested actions. Copy/paste to your chosen channel; sending is manual in this milestone.
            </div>
          </div>

          <div className="rounded-md border border-gray-200 bg-white shadow-sm p-4">
            <div className="flex items-center justify-between">
              <div className="font-semibold">Latest suggestion</div>
              {result?.action_id && (
                <span className="rounded-md bg-gray-100 px-2 py-1 text-2xs text-gray-700">
                  Action: {result.action_id}
                </span>
              )}
            </div>
            {result ? (
              <div className="mt-2 space-y-2 text-sm">
                <div className="text-xs text-gray-600">Type: {result.suggestion.message_type}</div>
                {result.suggestion.llm_used !== undefined && (
                  <div className="text-xs text-gray-600">
                    {result.suggestion.llm_used
                      ? "Generated with AI – RCIC review required."
                      : "Template-based draft – RCIC review required."}
                  </div>
                )}
                {result.suggestion.subject && <div className="font-semibold">{result.suggestion.subject}</div>}
                {result.suggestion.body && (
                  <pre className="whitespace-pre-wrap rounded-md bg-gray-50 p-3 text-xs border border-gray-100">
                    {result.suggestion.body}
                  </pre>
                )}
                {result.suggestion.missing_sections && result.suggestion.missing_sections.length > 0 && (
                  <div>
                    <div className="text-xs font-semibold text-gray-700">Missing sections</div>
                    <ul className="list-disc pl-4 text-xs text-gray-700">
                      {result.suggestion.missing_sections.map((m) => (
                        <li key={m}>{m}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {result.suggestion.missing_documents && result.suggestion.missing_documents.length > 0 && (
                  <div>
                    <div className="text-xs font-semibold text-gray-700">Missing documents</div>
                    <ul className="list-disc pl-4 text-xs text-gray-700">
                      {result.suggestion.missing_documents.map((m) => (
                        <li key={m}>{m}</li>
                      ))}
                    </ul>
                  </div>
                )}
                <div className="text-xs text-gray-600">
                  Status: Suggested (not sent). RCIC review required. Risk: {result.suggestion.risk_level || "n/a"}
                </div>
              </div>
            ) : (
              <div className="mt-3 text-sm text-gray-600">Generate a draft to see it here.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

