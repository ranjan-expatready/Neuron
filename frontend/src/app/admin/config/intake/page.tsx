"use client";

import { useEffect, useMemo, useState } from "react";

type Field = {
  id: string;
  label: string;
  data_path: string;
  type: string;
  ui_control?: string | null;
  required?: boolean | null;
  group?: string | null;
};

type Template = {
  id: string;
  label: string;
  applicable_programs: string[];
  applicable_plans: string[];
  steps: { id: string; label: string; fields: string[] | Field[] }[];
};

type DocumentDef = {
  id: string;
  label: string;
  category: string;
  required_for_programs: string[];
  required_when: any[];
};

type FormDef = {
  id: string;
  label: string;
  applicable_programs: string[];
  field_mappings: Record<string, string>;
};

type OptionSet = Record<string, { value: any; label: string }[]>;

const panelClass = "border rounded-md border-gray-200 bg-white shadow-sm";

export default function AdminIntakeConfigPage() {
  const [activeTab, setActiveTab] = useState<"fields" | "templates" | "documents" | "forms">("fields");
  const [fields, setFields] = useState<Field[]>([]);
  const [templates, setTemplates] = useState<Template[]>([]);
  const [documents, setDocuments] = useState<DocumentDef[]>([]);
  const [forms, setForms] = useState<FormDef[]>([]);
  const [options, setOptions] = useState<OptionSet>({});
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const loadAll = async () => {
      setLoading(true);
      setError(null);
      try {
        const [fieldsRes, templatesRes, docsRes, formsRes, optionsRes] = await Promise.all([
          fetch("/api/v1/admin/intake/fields"),
          fetch("/api/v1/admin/intake/templates?resolved=true"),
          fetch("/api/v1/admin/intake/documents"),
          fetch("/api/v1/admin/intake/forms"),
          fetch("/api/v1/admin/intake/options"),
        ]);
        if (![fieldsRes, templatesRes, docsRes, formsRes, optionsRes].every((r) => r.ok)) {
          throw new Error("One or more admin intake config requests failed");
        }
        setFields(await fieldsRes.json());
        setTemplates(await templatesRes.json());
        setDocuments(await docsRes.json());
        setForms(await formsRes.json());
        setOptions(await optionsRes.json());
      } catch (err) {
        console.error(err);
        setError("Unable to load admin intake config. Check your permissions or backend status.");
      } finally {
        setLoading(false);
      }
    };
    void loadAll();
  }, []);

  const fieldMap = useMemo(() => Object.fromEntries(fields.map((f) => [f.id, f])), [fields]);

  const renderFields = () => (
    <div className={panelClass}>
      <div className="border-b px-4 py-3 font-semibold">Field Dictionary</div>
      <div className="max-h-[70vh] overflow-y-auto divide-y">
        {fields.map((f) => (
          <div key={f.id} className="px-4 py-3 text-sm">
            <div className="flex items-center justify-between">
              <div className="font-semibold text-gray-900">{f.label}</div>
              <span className="rounded-md bg-gray-100 px-2 py-1 text-2xs text-gray-700">{f.id}</span>
            </div>
            <div className="text-xs text-gray-600">
              {f.data_path} • {f.type} {f.ui_control ? `(${f.ui_control})` : ""} {f.required ? "• required" : ""}
              {f.group ? ` • group: ${f.group}` : ""}
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderTemplates = () => (
    <div className={panelClass}>
      <div className="border-b px-4 py-3 font-semibold">Intake Templates</div>
      <div className="space-y-3 p-4">
        {templates.map((tpl) => (
          <div key={tpl.id} className="rounded-md border border-gray-200 p-3">
            <div className="flex items-center justify-between text-sm">
              <div>
                <div className="font-semibold text-gray-900">{tpl.label}</div>
                <div className="text-xs text-gray-600">
                  Programs: {tpl.applicable_programs.join(", ") || "—"} | Plans:{" "}
                  {tpl.applicable_plans.join(", ") || "—"}
                </div>
              </div>
              <span className="rounded-md bg-gray-100 px-2 py-1 text-2xs text-gray-700">{tpl.id}</span>
            </div>
            <div className="mt-2 space-y-2">
              {tpl.steps.map((step) => (
                <div key={step.id} className="rounded-md bg-gray-50 p-2">
                  <div className="text-sm font-semibold text-gray-800">{step.label}</div>
                  <ul className="mt-1 text-xs text-gray-700 space-y-1">
                    {(step.fields as any[]).map((fld) => {
                      const def: Field | undefined = typeof fld === "string" ? fieldMap[fld] : fld;
                      if (!def) return <li key={typeof fld === "string" ? fld : fld.id}>{String(fld)}</li>;
                      return (
                        <li key={def.id}>
                          {def.label} <span className="text-gray-500">({def.id})</span>
                        </li>
                      );
                    })}
                  </ul>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderDocuments = () => (
    <div className={panelClass}>
      <div className="border-b px-4 py-3 font-semibold">Document Matrix</div>
      <div className="space-y-3 p-4">
        {documents.map((doc) => (
          <div key={doc.id} className="rounded-md border border-gray-200 p-3 text-sm">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-semibold text-gray-900">{doc.label}</div>
                <div className="text-xs text-gray-600">Category: {doc.category}</div>
              </div>
              <span className="rounded-md bg-gray-100 px-2 py-1 text-2xs text-gray-700">{doc.id}</span>
            </div>
            <div className="mt-1 text-xs text-gray-600">
              Required for programs: {doc.required_for_programs?.join(", ") || "—"}
            </div>
            {doc.required_when?.length ? (
              <div className="mt-2 text-xs text-gray-700">
                Conditions:
                <ul className="list-disc pl-5">
                  {doc.required_when.map((cond: any, idx: number) => (
                    <li key={idx}>
                      {cond.field}{" "}
                      {Object.entries(cond)
                        .filter(([k]) => k !== "field")
                        .map(([k, v]) => `${k} ${Array.isArray(v) ? v.join(",") : v}`)
                        .join(" ")}
                    </li>
                  ))}
                </ul>
              </div>
            ) : null}
          </div>
        ))}
      </div>
    </div>
  );

  const renderForms = () => (
    <div className={panelClass}>
      <div className="border-b px-4 py-3 font-semibold">Forms</div>
      <div className="space-y-3 p-4">
        {forms.map((form) => (
          <div key={form.id} className="rounded-md border border-gray-200 p-3 text-sm">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-semibold text-gray-900">{form.label}</div>
                <div className="text-xs text-gray-600">
                  Programs: {form.applicable_programs?.join(", ") || "—"}
                </div>
              </div>
              <span className="rounded-md bg-gray-100 px-2 py-1 text-2xs text-gray-700">{form.id}</span>
            </div>
            <div className="mt-2 text-xs text-gray-700">
              Field mappings:
              <ul className="mt-1 space-y-1">
                {Object.entries(form.field_mappings || {}).map(([k, v]) => (
                  <li key={k}>
                    <span className="font-semibold">{k}</span> → {v}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <div className="mx-auto max-w-6xl px-4 py-8">
        <div className="rounded-md border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-900 mb-4">
          <div className="font-semibold">Admin Intake Config – Read-only</div>
          <div>Displays current field dictionary, templates, documents, and form mappings from domain configs.</div>
          {options && Object.keys(options).length > 0 ? (
            <div className="text-xs text-blue-800 mt-1">
              Option sets loaded: {Object.keys(options).slice(0, 4).join(", ")}
              {Object.keys(options).length > 4 ? "…" : ""}
            </div>
          ) : null}
          <div className="mt-2 text-xs">
            Draft/edit layer lives at{" "}
            <a className="text-blue-700 underline" href="/admin/config/intake/drafts">
              /admin/config/intake/drafts
            </a>{" "}
            (M7.2). Runtime still uses YAML until M7.3 activation.
          </div>
        </div>

        <div className="mb-3 flex gap-2">
          {(["fields", "templates", "documents", "forms"] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`rounded-md px-3 py-2 text-sm font-medium ${
                activeTab === tab ? "bg-blue-600 text-white" : "bg-white text-gray-700 border border-gray-200"
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        {error && <div className="mb-3 rounded-md border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700">{error}</div>}
        {loading ? <div className="text-sm text-gray-600">Loading admin intake config…</div> : null}

        {!loading && (
          <div>
            {activeTab === "fields" && renderFields()}
            {activeTab === "templates" && renderTemplates()}
            {activeTab === "documents" && renderDocuments()}
            {activeTab === "forms" && renderForms()}
          </div>
        )}
      </div>
    </div>
  );
}

