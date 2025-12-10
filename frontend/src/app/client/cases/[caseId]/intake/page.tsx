"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { useParams, useRouter } from "next/navigation";

import { IntakeFormRenderer, IntakeSchema } from "../../../../../components/IntakeFormRenderer";
import { apiClient } from "../../../../../lib/api-client";
import { useAuth } from "../../../../../lib/auth-context";

type ChecklistItem = {
  id: string;
  label: string;
  category: string;
  required: boolean;
  reasons: string[];
  status?: "uploaded" | "missing";
  files?: { id: string; filename: string }[];
};

const panelClass = "rounded-md border border-gray-200 bg-white shadow-sm p-4";

function getValueFromPath(obj: Record<string, any>, path: string): any {
  const parts = path.split(".");
  let cursor: any = obj;
  let startIdx = 0;
  if (parts[0] === "profile") {
    cursor = obj.profile || {};
    startIdx = 1;
  }
  for (let i = startIdx; i < parts.length; i++) {
    const part = parts[i];
    if (cursor == null || typeof cursor !== "object") return undefined;
    cursor = cursor[part];
  }
  return cursor;
}

export default function ClientCaseIntakePage() {
  const params = useParams();
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();
  const caseId = params?.caseId as string;

  const [loading, setLoading] = useState(true);
  const [schema, setSchema] = useState<IntakeSchema | null>(null);
  const [checklist, setChecklist] = useState<ChecklistItem[]>([]);
  const [initialValues, setInitialValues] = useState<Record<string, any>>({});
  const [programCode, setProgramCode] = useState<string>("EE_FSW");
  const [planCode, setPlanCode] = useState<string | undefined>(undefined);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [optionsCache, setOptionsCache] = useState<Record<string, { value: any; label: string }[]>>({});

  useEffect(() => {
    if (authLoading) return;
    if (!user) {
      router.push("/auth/login");
      return;
    }
  }, [user, authLoading, router]);

  useEffect(() => {
    if (!caseId || authLoading) return;
    const load = async () => {
      try {
        const caseData = await apiClient.getCase(caseId);
        const profileData = await apiClient.getCaseProfile(caseId);
        const program =
          caseData.case_metadata?.program_code ||
          caseData.case_metadata?.program ||
          caseData.case_metadata?.selected_program ||
          programCode;
        const plan = caseData.case_metadata?.plan_code || planCode;

        setProgramCode(program);
        setPlanCode(plan);

        const schemaData = await apiClient.getIntakeSchema({ program_code: program, plan_code: plan });
        setSchema(schemaData);

        if (schemaData?.steps?.length && profileData?.profile) {
          const values: Record<string, any> = {};
          schemaData.steps.forEach((step: any) => {
            step.fields.forEach((field: any) => {
              const value = getValueFromPath(profileData.profile as Record<string, any>, field.data_path);
              if (value !== undefined) {
                values[field.id] = value;
              }
            });
          });
          setInitialValues(values);
        }

        const checklistData: ChecklistItem[] = await apiClient.getDocumentChecklist(caseId, program);
        const caseDocs = await apiClient.getCaseDocuments(caseId);
        const enriched = checklistData.map((item) => {
          const matches = caseDocs.filter(
            (doc: any) =>
              doc.document_type === item.id ||
              doc.category === item.category ||
              doc.title?.toLowerCase().includes(item.label?.toLowerCase() || ""),
          );
          return {
            ...item,
            status: matches.length > 0 ? "uploaded" : "missing",
            files: matches.map((d: any) => ({ id: d.id, filename: d.original_filename || d.filename })),
          };
        });
        setChecklist(enriched);
      } catch (err) {
        console.error(err);
        setError("Unable to load intake. Please try again.");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [caseId, authLoading]);

  const onSubmit = async (payload: Record<string, any>) => {
    setSaving(true);
    setError(null);
    try {
      await apiClient.updateCaseProfile(caseId, payload.profile || payload);
    } catch (err) {
      console.error(err);
      setError("Could not save your intake. Please retry.");
    } finally {
      setSaving(false);
    }
  };

  const resolveOptionsRef = async (ref: string) => {
    if (optionsCache[ref]) return optionsCache[ref];
    const opts = await apiClient.getIntakeOptions(ref);
    setOptionsCache((prev) => ({ ...prev, [ref]: opts }));
    return opts;
  };

  const checklistRequired = useMemo(() => checklist.filter((c) => c.required), [checklist]);
  const checklistOptional = useMemo(() => checklist.filter((c) => !c.required), [checklist]);

  if (authLoading || loading) {
    return <div className="p-6 text-sm text-gray-600">Loading...</div>;
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">{error}</div>
      </div>
    );
  }

  if (!schema) {
    return (
      <div className="p-6">
        <div className="rounded-md border border-yellow-200 bg-yellow-50 px-4 py-3 text-sm text-yellow-800">
          We could not load your intake right now.
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs uppercase text-gray-500">Client Intake</p>
          <h1 className="text-2xl font-semibold text-gray-900">Tell us about yourself</h1>
          <p className="text-sm text-gray-600">
            Your answers populate your profile and help us prepare the right documents.
          </p>
        </div>
        {saving ? <span className="text-sm text-gray-600">Saving…</span> : null}
      </div>

      <div className="flex items-center gap-4">
        <div>
          <label className="text-sm font-medium text-gray-700">Program</label>
          <select
            className="mt-1 block rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:ring-blue-500"
            value={programCode}
            onChange={(e) => setProgramCode(e.target.value)}
          >
            <option value="EE_FSW">Express Entry - FSW</option>
            <option value="EE_CEC">Express Entry - CEC</option>
            <option value="EE_FST">Express Entry - FST</option>
          </select>
        </div>
        {planCode ? (
          <div>
            <label className="text-sm font-medium text-gray-700">Plan</label>
            <input
              className="mt-1 block rounded-md border border-gray-200 px-3 py-2 text-sm shadow-sm bg-gray-50"
              value={planCode}
              readOnly
            />
          </div>
        ) : null}
      </div>

      <IntakeFormRenderer
        schema={schema}
        initialValues={initialValues}
        onSubmit={onSubmit}
        resolveOptionsRef={resolveOptionsRef}
      />

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <div className={panelClass}>
          <h3 className="text-base font-semibold text-gray-800">Required documents</h3>
          <ul className="mt-3 space-y-2">
            {checklistRequired.length === 0 ? (
              <li className="text-sm text-gray-500">No required documents yet.</li>
            ) : (
              checklistRequired.map((item) => (
                <li key={item.id} className="rounded-md border border-gray-200 p-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-semibold text-gray-900">{item.label || item.id}</p>
                      <p className="text-xs text-gray-600">{item.category}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <span
                        className={`rounded-full px-2 py-1 text-2xs font-semibold ${
                          item.status === "uploaded"
                            ? "bg-green-100 text-green-700"
                            : "bg-red-100 text-red-700"
                        }`}
                      >
                        {item.status === "uploaded" ? "Uploaded" : "Missing"}
                      </span>
                      <Link
                        href={`/cases/${caseId}/upload`}
                        className="text-xs font-semibold text-blue-600 hover:underline"
                      >
                        Manage uploads
                      </Link>
                    </div>
                  </div>
                  {item.reasons?.length ? (
                    <p className="mt-1 text-xs text-gray-600">Why: {item.reasons.join("; ")}</p>
                  ) : null}
                  {item.files?.length ? (
                    <p className="mt-2 text-xs text-gray-700">Files: {item.files.map((f) => f.filename).join(", ")}</p>
                  ) : null}
                </li>
              ))
            )}
          </ul>
        </div>

        <div className={panelClass}>
          <h3 className="text-base font-semibold text-gray-800">Optional documents</h3>
          <ul className="mt-3 space-y-2">
            {checklistOptional.length === 0 ? (
              <li className="text-sm text-gray-500">No optional documents.</li>
            ) : (
              checklistOptional.map((item) => (
                <li key={item.id} className="rounded-md border border-gray-200 p-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-semibold text-gray-900">{item.label || item.id}</p>
                      <p className="text-xs text-gray-600">{item.category}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <span
                        className={`rounded-full px-2 py-1 text-2xs font-semibold ${
                          item.status === "uploaded" ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-700"
                        }`}
                      >
                        {item.status === "uploaded" ? "Uploaded" : "Missing"}
                      </span>
                      <Link
                        href={`/cases/${caseId}/upload`}
                        className="text-xs font-semibold text-blue-600 hover:underline"
                      >
                        Manage uploads
                      </Link>
                    </div>
                  </div>
                  {item.files?.length ? (
                    <p className="mt-2 text-xs text-gray-700">Files: {item.files.map((f) => f.filename).join(", ")}</p>
                  ) : null}
                </li>
              ))
            )}
          </ul>
        </div>
      </div>
    </div>
  );
}

