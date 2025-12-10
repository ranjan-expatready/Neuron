import { useMemo, useState } from "react";

type IntakeField = {
  id: string;
  label: string;
  data_path: string;
  type: string;
  ui_control?: string | null;
  options_ref?: string[] | string | null;
  validations?: Record<string, any>;
  help_text?: string | null;
  required?: boolean | null;
};

type IntakeStep = {
  id: string;
  label: string;
  fields: IntakeField[];
};

export type IntakeSchema = {
  program_code: string;
  plan_code?: string | null;
  template_id: string;
  label: string;
  steps: IntakeStep[];
};

export type IntakeFormRendererProps = {
  schema: IntakeSchema;
  initialValues?: Record<string, any>;
  onSubmit: (values: Record<string, any>) => Promise<void> | void;
};

type FieldErrors = Record<string, string>;

function setNested(target: Record<string, any>, path: string, value: any) {
  const parts = path.split(".");
  let cursor = target;
  let startIdx = 0;
  if (parts[0] === "profile") {
    cursor.profile = cursor.profile || {};
    cursor = cursor.profile;
    startIdx = 1;
  }
  for (let idx = startIdx; idx < parts.length; idx++) {
    const part = parts[idx];
    if (idx === parts.length - 1) {
      cursor[part] = value;
      return;
    }
    if (!cursor[part] || typeof cursor[part] !== "object") {
      cursor[part] = {};
    }
    cursor = cursor[part];
  }
}

export function IntakeFormRenderer({ schema, initialValues = {}, onSubmit }: IntakeFormRendererProps) {
  const [values, setValues] = useState<Record<string, any>>(initialValues);
  const [errors, setErrors] = useState<FieldErrors>({});
  const [submitting, setSubmitting] = useState(false);

  const fieldList = useMemo(() => schema.steps.flatMap((s) => s.fields), [schema.steps]);
  const fieldById = useMemo(() => Object.fromEntries(fieldList.map((f) => [f.id, f])), [fieldList]);

  const validate = (): boolean => {
    const nextErrors: FieldErrors = {};
    fieldList.forEach((field) => {
      const val = values[field.id];
      const v = field.validations || {};
      if (field.required && (val === undefined || val === null || val === "")) {
        nextErrors[field.id] = "This field is required.";
        return;
      }
      if (v.min_length && typeof val === "string" && val.length < v.min_length) {
        nextErrors[field.id] = `Minimum length is ${v.min_length}`;
      }
      if (v.max_length && typeof val === "string" && val.length > v.max_length) {
        nextErrors[field.id] = `Maximum length is ${v.max_length}`;
      }
      if (v.min !== undefined && val !== undefined && val !== null && Number(val) < v.min) {
        nextErrors[field.id] = `Minimum value is ${v.min}`;
      }
      if (v.max !== undefined && val !== undefined && val !== null && Number(val) > v.max) {
        nextErrors[field.id] = `Maximum value is ${v.max}`;
      }
    });
    setErrors(nextErrors);
    return Object.keys(nextErrors).length === 0;
  };

  const handleChange = (fieldId: string, value: any) => {
    setValues((prev) => ({ ...prev, [fieldId]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    setSubmitting(true);
    try {
      const payload: Record<string, any> = {};
      Object.entries(values).forEach(([fieldId, value]) => {
        const def = fieldById[fieldId];
        if (!def) return;
        setNested(payload, def.data_path, value);
      });
      await onSubmit(payload);
    } finally {
      setSubmitting(false);
    }
  };

  const renderField = (field: IntakeField) => {
    const value = values[field.id] ?? "";
    const commonProps = {
      id: field.id,
      name: field.id,
      value,
      onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) =>
        handleChange(field.id, e.target.type === "checkbox" ? (e.target as HTMLInputElement).checked : e.target.value),
      className:
        "mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:ring-blue-500",
    };

    switch (field.ui_control) {
      case "number":
        return <input type="number" {...commonProps} />;
      case "date":
        return <input type="date" {...commonProps} />;
      case "select": {
        const options =
          Array.isArray(field.options_ref) ? field.options_ref : typeof field.options_ref === "string"
            ? []
            : [];
        return (
          <select {...commonProps}>
            <option value="">Select...</option>
            {options.map((opt) => (
              <option key={opt} value={opt}>
                {opt}
              </option>
            ))}
          </select>
        );
      }
      case "checkbox":
        return (
          <input
            type="checkbox"
            id={field.id}
            name={field.id}
            checked={!!values[field.id]}
            onChange={(e) => handleChange(field.id, e.target.checked)}
            className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
        );
      case "text":
      default:
        return <input type="text" {...commonProps} />;
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="flex flex-col gap-6 lg:flex-row">
        <div className="w-full lg:w-1/4">
          <div className="sticky top-4 rounded-md border border-gray-200 bg-white p-4 shadow-sm">
            <h3 className="text-sm font-semibold text-gray-700">Steps</h3>
            <ol className="mt-3 space-y-2 text-sm text-gray-700">
              {schema.steps.map((step, idx) => (
                <li key={step.id} className="flex items-center gap-2">
                  <span className="flex h-6 w-6 items-center justify-center rounded-full bg-blue-100 text-xs font-semibold text-blue-700">
                    {idx + 1}
                  </span>
                  <span>{step.label}</span>
                </li>
              ))}
            </ol>
          </div>
        </div>
        <div className="w-full lg:w-3/4 space-y-6">
          {schema.steps.map((step) => (
            <div key={step.id} className="rounded-md border border-gray-200 bg-white p-4 shadow-sm">
              <h4 className="text-base font-semibold text-gray-800">{step.label}</h4>
              <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2">
                {step.fields.map((field) => (
                  <div key={field.id} className="flex flex-col">
                    <label htmlFor={field.id} className="text-sm font-medium text-gray-700">
                      {field.label}
                      {field.required ? <span className="text-red-500">*</span> : null}
                    </label>
                    {renderField(field)}
                    {field.help_text ? (
                      <p className="mt-1 text-xs text-gray-500">{field.help_text}</p>
                    ) : null}
                    {errors[field.id] ? (
                      <p className="mt-1 text-xs text-red-600">{errors[field.id]}</p>
                    ) : null}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
      <div className="flex justify-end">
        <button
          type="submit"
          disabled={submitting}
          className="inline-flex items-center rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
        >
          {submitting ? "Saving..." : "Save intake"}
        </button>
      </div>
    </form>
  );
}

