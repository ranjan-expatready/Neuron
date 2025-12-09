"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { apiClient } from "@/lib/api-client";
import { extractApiErrorMessage } from "@/lib/error-helpers";

export default function NewCasePage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [form, setForm] = useState({
    personFirstName: "",
    personLastName: "",
    personEmail: "",
    caseTitle: "",
    caseType: "EXPRESS_ENTRY_FSW",
    caseDescription: "",
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/auth/login");
    }
  }, [authLoading, user, router]);

  if (authLoading || !user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const handleChange =
    (field: keyof typeof form) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
      setForm((prev) => ({ ...prev, [field]: e.target.value }));
    };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError("");

    try {
      if (!form.personFirstName || !form.personLastName) {
        throw new Error("Client first and last name are required");
      }
      if (!form.caseType || !form.caseTitle) {
        throw new Error("Case type and title are required");
      }

      const person = await apiClient.createPerson({
        first_name: form.personFirstName,
        last_name: form.personLastName,
        email: form.personEmail || undefined,
      });

      const createdCase = await apiClient.createCase({
        primary_person_id: person.id,
        case_type: form.caseType,
        title: form.caseTitle,
        description: form.caseDescription || undefined,
        priority: "normal",
      });

      router.push(`/cases/${createdCase.id}`);
    } catch (err: any) {
      setError(extractApiErrorMessage(err, "Failed to create case"));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-secondary-50">
      <header className="bg-white shadow-sm border-b border-secondary-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="py-6">
            <h1
              className="text-2xl font-bold text-secondary-900"
              data-testid="new-case-heading"
            >
              Create New Case
            </h1>
            <p className="text-secondary-500">
              Provide client information and basic case details.
            </p>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <form className="space-y-8" onSubmit={handleSubmit}>
          {error && (
            <div
              className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md"
              data-testid="new-case-error"
            >
              {error}
            </div>
          )}

          <div className="card space-y-4">
            <h2 className="text-lg font-semibold text-secondary-900">
              Client Information
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="form-label" htmlFor="personFirstName">
                  First Name
                </label>
                <input
                  id="personFirstName"
                  type="text"
                  className="form-input"
                  value={form.personFirstName}
                  onChange={handleChange("personFirstName")}
                  data-testid="new-case-person-first-name"
                  required
                />
              </div>
              <div>
                <label className="form-label" htmlFor="personLastName">
                  Last Name
                </label>
                <input
                  id="personLastName"
                  type="text"
                  className="form-input"
                  value={form.personLastName}
                  onChange={handleChange("personLastName")}
                  data-testid="new-case-person-last-name"
                  required
                />
              </div>
            </div>
            <div>
              <label className="form-label" htmlFor="personEmail">
                Email (optional)
              </label>
              <input
                id="personEmail"
                type="email"
                className="form-input"
                value={form.personEmail}
                onChange={handleChange("personEmail")}
                data-testid="new-case-person-email"
              />
            </div>
          </div>

          <div className="card space-y-4">
            <h2 className="text-lg font-semibold text-secondary-900">
              Case Details
            </h2>
            <div>
              <label className="form-label" htmlFor="caseTitle">
                Case Title
              </label>
              <input
                id="caseTitle"
                type="text"
                className="form-input"
                value={form.caseTitle}
                onChange={handleChange("caseTitle")}
                data-testid="new-case-title"
                required
              />
            </div>
            <div>
              <label className="form-label" htmlFor="caseType">
                Case Type
              </label>
              <input
                id="caseType"
                type="text"
                className="form-input"
                value={form.caseType}
                onChange={handleChange("caseType")}
                data-testid="new-case-type"
                required
              />
            </div>
            <div>
              <label className="form-label" htmlFor="caseDescription">
                Description
              </label>
              <textarea
                id="caseDescription"
                className="form-input"
                rows={4}
                value={form.caseDescription}
                onChange={handleChange("caseDescription")}
                data-testid="new-case-description"
              />
            </div>
          </div>

          <div className="flex justify-end space-x-4">
            <button
              type="button"
              className="btn btn-outline"
              onClick={() => router.push("/cases")}
              data-testid="new-case-cancel"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={submitting}
              data-testid="new-case-submit"
            >
              {submitting ? "Creating..." : "Create Case"}
            </button>
          </div>
        </form>
      </main>
    </div>
  );
}
