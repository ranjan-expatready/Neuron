"use client";

import { useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";

import { IntakeFormRenderer, IntakeSchema } from "../../../../components/IntakeFormRenderer";
import { apiClient } from "../../../../lib/api-client";

type CaseResponse = {
  id: string;
  case_type?: string;
  form_data?: Record<string, any>;
  case_metadata?: Record<string, any>;
};

type ChecklistItem = {
  id: string;
  label: string;
  category: string;
  required: boolean;
  reasons: string[];
};

const panelClass = "rounded-md border border-gray-200 bg-white shadow-sm p-4";

function getValueFromPath(obj: Record<string, any>, path: string): any {
  const parts = path.startsWith("profile.") ? path.split(".").slice(1) : path.split(".");
  let cursor: any = obj;
  for (const part of parts) {
    if (cursor == null || typeof cursor !== "object") return undefined;
    cursor = cursor[part];
  }
  return cursor;
}

export default function CaseIntakePage() {
  const params = useParams();
  const caseId = params?.caseId as string;
  const [loading, setLoading] = useState(true);
  const [schema, setSchema] = useState<IntakeSchema | null>(null);
  const [checklist, setChecklist] = useState<ChecklistItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [initialValues, setInitialValues] = useState<Record<string, any>>({});
  const [programCode, setProgramCode] = useState<string>("EE_FSW");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const caseData: CaseResponse = await apiClient.getCase(caseId);
        const program =
          caseData.case_metadata?.program_code ||
          caseData.case_metadata?.program ||
          caseData.case_metadata?.selected_program ||
          "EE_FSW";
        setProgramCode(program);

        const schemaData = await apiClient.getIntakeSchema({ program_code: program });
        setSchema(schemaData);

        // Map stored form_data back to field ids when possible
        if (schemaData?.steps?.length && caseData.form_data) {
          const values: Record<string, any> = {};
          schemaData.steps.forEach((step: any) => {
            step.fields.forEach((field: any) => {
              const value = getValueFromPath(caseData.form_data as Record<string, any>, field.data_path);
              if (value !== undefined) {
                values[field.id] = value;
              }
            });
          });
          setInitialValues(values);
        }

        const checklistData: ChecklistItem[] = await apiClient.getDocumentChecklist(caseId, program);
        setChecklist(checklistData);
      } catch (err) {
        console.error("Failed to load intake data", err);
        setError("Unable to load intake schema or checklist. Please ensure backend is reachable.");
      } finally {
        setLoading(false);
      }
    };

    if (caseId) {
      fetchData();
    }
  }, [caseId]);

  const onSubmit = async (payload: Record<string, any>) => {
    setSaving(true);
    setError(null);
    try {
      // Persist into case form_data for now (TODO: align with canonical profile API when exposed)
      await apiClient.updateCase(caseId, {
        form_data: { profile: payload.profile || payload },
        metadata: { program_code: programCode },
      });
    } catch (err) {
      console.error("Failed to save intake", err);
      setError("Saving intake failed. Please retry.");
    } finally {
      setSaving(false);
    }
  };

  const checklistRequired = useMemo(() => checklist.filter((c) => c.required), [checklist]);
  const checklistOptional = useMemo(() => checklist.filter((c) => !c.required), [checklist]);

  if (loading) {
    return <div className="p-6 text-sm text-gray-600">Loading intake...</div>;
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
          No intake schema available.
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs uppercase text-gray-500">Case Intake</p>
          <h1 className="text-2xl font-semibold text-gray-900">Schema-driven intake ({programCode})</h1>
          <p className="text-sm text-gray-600">Rendered from /api/v1/intake-schema and saved to case form data.</p>
        </div>
        {saving ? <span className="text-sm text-gray-600">Saving...</span> : null}
      </div>

      <IntakeFormRenderer schema={schema} initialValues={initialValues} onSubmit={onSubmit} />

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <div className={panelClass}>
          <h3 className="text-base font-semibold text-gray-800">Required documents</h3>
          <ul className="mt-3 space-y-2">
            {checklistRequired.length === 0 ? (
              <li className="text-sm text-gray-500">No required documents.</li>
            ) : (
              checklistRequired.map((item) => (
                <li key={item.id} className="rounded-md border border-gray-200 p-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-semibold text-gray-900">{item.label || item.id}</p>
                      <p className="text-xs text-gray-600">{item.category}</p>
                    </div>
                    <span className="text-xs font-semibold text-red-600">Required</span>
                  </div>
                  {item.reasons?.length ? (
                    <p className="mt-1 text-xs text-gray-600">Reasons: {item.reasons.join("; ")}</p>
                  ) : null}
                  <p className="mt-2 text-xs text-blue-600">
                    TODO: link to document upload and reflect upload status.
                  </p>
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
                    <span className="text-xs font-semibold text-gray-600">Optional</span>
                  </div>
                  {item.reasons?.length ? (
                    <p className="mt-1 text-xs text-gray-600">Reasons: {item.reasons.join("; ")}</p>
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

