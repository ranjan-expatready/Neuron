"use client";

import { useEffect, useState } from "react";

type FormFieldAutofill = {
  form_id: string;
  field_id: string;
  proposed_value: any;
  source_type: string;
  source_path?: string | null;
  notes?: string | null;
};

type FormAutofillResult = {
  form_id: string;
  fields: FormFieldAutofill[];
  warnings: string[];
};

type Preview = {
  bundle_id?: string | null;
  forms: FormAutofillResult[];
  warnings: string[];
};

async function fetchPreview(caseId: string): Promise<Preview> {
  const res = await fetch(`/api/v1/cases/${caseId}/forms/autofill-preview`);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Failed to load preview (${res.status})`);
  }
  return res.json();
}

export default function FormsAutofillPage({ params }: { params: { caseId: string } }) {
  const { caseId } = params;
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [preview, setPreview] = useState<Preview | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchPreview(caseId);
      setPreview(data);
    } catch (err: any) {
      setError(err.message || "Failed to load form autofill preview");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load().catch(() => null);
  }, [caseId]);

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <div className="mx-auto max-w-4xl px-4 py-8 space-y-4">
        <div className="rounded border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
          <div className="font-semibold">Form Autofill PREVIEW (Shadow)</div>
          <div>Draft-only preview. RCIC must review and confirm before any submission. No PDFs or IRCC actions are performed.</div>
        </div>

        {error && <div className="rounded border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700">{error}</div>}

        <button
          className="rounded bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-60"
          onClick={load}
          disabled={loading}
        >
          {loading ? "Refreshing…" : "Refresh Preview"}
        </button>

        {preview && (
          <div className="space-y-3">
            {preview.warnings?.length > 0 && (
              <div className="rounded border border-yellow-200 bg-yellow-50 px-3 py-2 text-sm text-yellow-800">
                {preview.warnings.map((w, idx) => (
                  <div key={`warn-${idx}`}>{w}</div>
                ))}
              </div>
            )}
            {preview.forms.map((form) => (
              <div key={form.form_id} className="rounded border border-gray-200 bg-white p-4 shadow-sm space-y-2">
                <div className="flex items-center justify-between">
                  <div className="font-semibold text-sm">Form: {form.form_id}</div>
                  {form.warnings?.length > 0 && (
                    <div className="text-xs text-amber-800">{form.warnings.join("; ")}</div>
                  )}
                </div>
                <div className="space-y-2">
                  {form.fields.map((field) => (
                    <div key={`${form.form_id}-${field.field_id}`} className="rounded border border-gray-100 bg-gray-50 p-2 text-xs">
                      <div className="flex justify-between">
                        <span className="font-semibold">{field.field_id}</span>
                        <span className="rounded bg-blue-100 px-2 py-0.5 text-blue-800">{field.source_type}</span>
                      </div>
                      <div className="text-gray-800 break-words">
                        Value: {field.proposed_value === null || field.proposed_value === undefined ? "—" : JSON.stringify(field.proposed_value)}
                      </div>
                      {field.source_path && <div className="text-gray-600">Source path: {field.source_path}</div>}
                      {field.notes && <div className="text-gray-600">Notes: {field.notes}</div>}
                    </div>
                  ))}
                  {form.fields.length === 0 && <div className="text-xs text-gray-500">No fields mapped.</div>}
                </div>
              </div>
            ))}
            {preview.forms.length === 0 && <div className="text-sm text-gray-600">No forms available for this case/program.</div>}
          </div>
        )}
      </div>
    </div>
  );
}

