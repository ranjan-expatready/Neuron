"use client";

/**
 * Express Entry Case Intake UI (Read-Only) – Milestone 3.3
 * Plan:
 * - Route: /express-entry/intake
 * - Left/top: intake form capturing minimal profile fields (age, family size, education, language CLB, work experience, PoF, job offer).
 * - Right/bottom: results panel showing program eligibility (with reasons), CRS breakdown, and required forms/documents from Case Evaluation API.
 * - No persistence, no payments; single-session evaluation only.
 * - Config-first: display whatever the backend returns; do not hard-code IRCC thresholds.
 * - If API unreachable (401/403/network), show a banner and keep the form (no heavy mocks; only a small placeholder).
 */

import { useMemo, useState } from "react";

type EligibilityItem = {
  program_code: string;
  eligible: boolean;
  reasons: string[];
  rule_ids?: string[];
};

type CrsBreakdown = {
  total: number;
  breakdown: Record<string, number>;
  factor_details: { name: string; points: number; rule_id: string; config_ref?: string | null }[];
};

type DocumentRequirement = {
  id: string;
  label?: string | null;
  category?: string | null;
  mandatory?: boolean;
};

type EvaluationResponse = {
  program_eligibility: EligibilityItem[];
  crs: CrsBreakdown;
  documents_and_forms: {
    forms: string[];
    documents: DocumentRequirement[];
  };
  warnings: string[];
};

const bannerClass =
  "rounded-md border border-blue-200 bg-blue-50 text-blue-900 px-4 py-3 text-sm mb-4";
const panelClass = "border rounded-md border-gray-200 bg-white shadow-sm";
const labelClass = "block text-sm font-medium text-gray-700";
const inputClass =
  "mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:ring-blue-500";

export default function ExpressEntryIntakePage() {
  const [age, setAge] = useState<string>("");
  const [familySize, setFamilySize] = useState<string>("1");
  const [maritalStatus, setMaritalStatus] = useState<string>("single");
  const [educationLevel, setEducationLevel] = useState<string>("bachelor");
  const [languageTest, setLanguageTest] = useState<string>("IELTS");
  const [listening, setListening] = useState<string>("");
  const [reading, setReading] = useState<string>("");
  const [writing, setWriting] = useState<string>("");
  const [speaking, setSpeaking] = useState<string>("");
  const [canadianYears, setCanadianYears] = useState<string>("");
  const [foreignYears, setForeignYears] = useState<string>("");
  const [proofFunds, setProofFunds] = useState<string>("");
  const [jobOffer, setJobOffer] = useState<boolean>(false);
  const [jobTeer, setJobTeer] = useState<string>("0");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [warning, setWarning] = useState<string | null>(null);
  const [result, setResult] = useState<EvaluationResponse | null>(null);

  const buildProfilePayload = () => {
    const today = new Date();
    const approximateDob =
      age && !Number.isNaN(Number(age))
        ? new Date(today.getFullYear() - Number(age), today.getMonth(), today.getDate())
            .toISOString()
            .slice(0, 10)
        : undefined;

    const work_experience = [];
    if (canadianYears) {
      const years = Number(canadianYears);
      if (!Number.isNaN(years) && years > 0) {
        work_experience.push({
          is_canadian: true,
          teer_level: Number(jobTeer) || 0,
          is_continuous: true,
          start_date: new Date(today.getFullYear() - years, today.getMonth(), today.getDate())
            .toISOString()
            .slice(0, 10),
          end_date: today.toISOString().slice(0, 10),
        });
      }
    }
    if (foreignYears) {
      const years = Number(foreignYears);
      if (!Number.isNaN(years) && years > 0) {
        work_experience.push({
          is_canadian: false,
          teer_level: 2,
          is_continuous: true,
          start_date: new Date(today.getFullYear() - years, today.getMonth(), today.getDate())
            .toISOString()
            .slice(0, 10),
          end_date: today.toISOString().slice(0, 10),
        });
      }
    }

    const proof_of_funds =
      proofFunds && !Number.isNaN(Number(proofFunds))
        ? [
            {
              amount: Number(proofFunds),
              currency: "CAD",
              as_of_date: today.toISOString().slice(0, 10),
              exemption_reason: jobOffer ? "valid_job_offer" : undefined,
            },
          ]
        : [];

    const job_offers = jobOffer
      ? [
          {
            teer_level: Number(jobTeer) || 0,
            full_time: true,
            non_seasonal: true,
            duration_months: 12,
          },
        ]
      : [];

    return {
      first_name: "Case",
      last_name: "Applicant",
      date_of_birth: approximateDob,
      marital_status: maritalStatus,
      family_size: Number(familySize) || 1,
      education: [
        {
          level: educationLevel,
          eca_received: true,
        },
      ],
      language_tests: [
        {
          test_type: languageTest,
          listening_clb: listening ? Number(listening) : undefined,
          reading_clb: reading ? Number(reading) : undefined,
          writing_clb: writing ? Number(writing) : undefined,
          speaking_clb: speaking ? Number(speaking) : undefined,
        },
      ],
      work_experience,
      proof_of_funds,
      job_offers,
    };
  };

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setWarning(null);
    setResult(null);

    if (!age || !languageTest || !listening || !reading || !writing || !speaking) {
      setError("Please provide age and all language CLB scores.");
      return;
    }

    setLoading(true);
    try {
      const payload = { profile: buildProfilePayload() };
      const res = await fetch("/api/v1/cases/evaluate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        throw new Error(`Evaluation failed (${res.status})`);
      }
      const data: EvaluationResponse = await res.json();
      setResult(data);
      if (data.warnings?.length) {
        setWarning(data.warnings.join("; "));
      }
    } catch (err) {
      console.warn("Case Evaluation API unreachable or failed", err);
      setError(
        "Case Evaluation API is not reachable in this environment; please ensure the backend is running and you are authorized.",
      );
    } finally {
      setLoading(false);
    }
  };

  const eligibilitySummary = useMemo(() => result?.program_eligibility ?? [], [result]);
  const crsSummary = useMemo(() => result?.crs, [result]);
  const docSummary = useMemo(() => result?.documents_and_forms, [result]);

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <div className="mx-auto max-w-6xl px-4 py-8">
        <div className={bannerClass}>
          <div className="font-semibold">Express Entry Case Intake (Read-only, config-driven)</div>
          <div>Inputs are evaluated via backend Case Evaluation API; results reflect current domain configs.</div>
          <div className="text-xs text-gray-700">No data is persisted. No payments or edits in this view.</div>
        </div>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
          <section className="lg:col-span-5">
            <div className={panelClass}>
              <div className="border-b px-4 py-3 font-semibold">Intake</div>
              <form className="space-y-4 p-4" onSubmit={onSubmit}>
                <div>
                  <label className={labelClass} htmlFor="age">
                    Age
                  </label>
                  <input
                    id="age"
                    type="number"
                    min="18"
                    className={inputClass}
                    value={age}
                    onChange={(e) => setAge(e.target.value)}
                  />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className={labelClass} htmlFor="family-size">
                      Family size
                    </label>
                    <input
                      id="family-size"
                      type="number"
                      min="1"
                      className={inputClass}
                      value={familySize}
                      onChange={(e) => setFamilySize(e.target.value)}
                    />
                  </div>
                  <div>
                    <label className={labelClass} htmlFor="marital-status">
                      Marital status
                    </label>
                    <select
                      id="marital-status"
                      className={inputClass}
                      value={maritalStatus}
                      onChange={(e) => setMaritalStatus(e.target.value)}
                    >
                      <option value="single">Single</option>
                      <option value="married">Married</option>
                      <option value="common-law">Common-law</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className={labelClass} htmlFor="education-level">
                    Highest education
                  </label>
                  <select
                    id="education-level"
                    className={inputClass}
                    value={educationLevel}
                    onChange={(e) => setEducationLevel(e.target.value)}
                  >
                    <option value="secondary">Secondary</option>
                    <option value="bachelor">Bachelor</option>
                    <option value="masters">Masters</option>
                    <option value="phd">PhD</option>
                  </select>
                </div>

                <div>
                  <label className={labelClass} htmlFor="test-type">
                    Test type
                  </label>
                  <select
                    id="test-type"
                    className={inputClass}
                    value={languageTest}
                    onChange={(e) => setLanguageTest(e.target.value)}
                  >
                    <option value="IELTS">IELTS</option>
                    <option value="CELPIP">CELPIP</option>
                    <option value="TEF">TEF</option>
                    <option value="TCF">TCF</option>
                  </select>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className={labelClass} htmlFor="listening-clb">
                      Listening CLB
                    </label>
                    <input
                      id="listening-clb"
                      type="number"
                      min="1"
                      className={inputClass}
                      value={listening}
                      onChange={(e) => setListening(e.target.value)}
                    />
                  </div>
                  <div>
                    <label className={labelClass} htmlFor="reading-clb">
                      Reading CLB
                    </label>
                    <input
                      id="reading-clb"
                      type="number"
                      min="1"
                      className={inputClass}
                      value={reading}
                      onChange={(e) => setReading(e.target.value)}
                    />
                  </div>
                  <div>
                    <label className={labelClass} htmlFor="writing-clb">
                      Writing CLB
                    </label>
                    <input
                      id="writing-clb"
                      type="number"
                      min="1"
                      className={inputClass}
                      value={writing}
                      onChange={(e) => setWriting(e.target.value)}
                    />
                  </div>
                  <div>
                    <label className={labelClass} htmlFor="speaking-clb">
                      Speaking CLB
                    </label>
                    <input
                      id="speaking-clb"
                      type="number"
                      min="1"
                      className={inputClass}
                      value={speaking}
                      onChange={(e) => setSpeaking(e.target.value)}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className={labelClass} htmlFor="canadian-exp">
                      Canadian experience (years)
                    </label>
                    <input
                      id="canadian-exp"
                      type="number"
                      min="0"
                      className={inputClass}
                      value={canadianYears}
                      onChange={(e) => setCanadianYears(e.target.value)}
                    />
                  </div>
                  <div>
                    <label className={labelClass} htmlFor="foreign-exp">
                      Foreign experience (years)
                    </label>
                    <input
                      id="foreign-exp"
                      type="number"
                      min="0"
                      className={inputClass}
                      value={foreignYears}
                      onChange={(e) => setForeignYears(e.target.value)}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className={labelClass} htmlFor="proof-funds">
                      Proof of funds (CAD)
                    </label>
                    <input
                      id="proof-funds"
                      type="number"
                      min="0"
                      className={inputClass}
                      value={proofFunds}
                      onChange={(e) => setProofFunds(e.target.value)}
                    />
                  </div>
                  <div>
                    <label className={labelClass} htmlFor="job-offer">
                      Job offer (arranged employment)
                    </label>
                    <select
                      id="job-offer"
                      className={inputClass}
                      value={jobOffer ? "yes" : "no"}
                      onChange={(e) => setJobOffer(e.target.value === "yes")}
                    >
                      <option value="no">No</option>
                      <option value="yes">Yes</option>
                    </select>
                  </div>
                </div>

                {jobOffer && (
                  <div>
                    <label className={labelClass} htmlFor="job-teer">
                      Job offer TEER
                    </label>
                    <input
                      id="job-teer"
                      type="number"
                      min="0"
                      max="3"
                      className={inputClass}
                      value={jobTeer}
                      onChange={(e) => setJobTeer(e.target.value)}
                    />
                  </div>
                )}

                {error && <div className="text-sm text-red-700">{error}</div>}
                {warning && <div className="text-sm text-amber-700">{warning}</div>}

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow hover:bg-blue-700 disabled:opacity-60"
                >
                  {loading ? "Evaluating..." : "Evaluate my case"}
                </button>
              </form>
            </div>
          </section>

          <section className="lg:col-span-7">
            <div className={panelClass}>
              <div className="border-b px-4 py-3 font-semibold">Results</div>
              <div className="space-y-6 p-4">
                {!result && !error && (
                  <div className="text-sm text-gray-600">
                    Fill the intake form and click “Evaluate my case” to see program eligibility, CRS breakdown, and required
                    forms/documents.
                  </div>
                )}

                {result && (
                  <>
                    <div>
                      <div className="text-base font-semibold">Program eligibility</div>
                      <div className="mt-2 space-y-2">
                        {eligibilitySummary.map((item) => (
                          <div
                            key={item.program_code}
                            className="rounded border border-gray-200 bg-gray-50 px-3 py-2 text-sm"
                          >
                            <div className="flex items-center justify-between">
                              <span className="font-semibold">{item.program_code}</span>
                              <span
                                className={`rounded px-2 py-0.5 text-xs font-semibold ${
                                  item.eligible ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
                                }`}
                              >
                                {item.eligible ? "Eligible" : "Not eligible"}
                              </span>
                            </div>
                            {item.reasons?.length ? (
                              <ul className="mt-2 list-disc space-y-1 pl-5 text-gray-700">
                                {item.reasons.map((reason, idx) => (
                                  <li key={idx}>{reason}</li>
                                ))}
                              </ul>
                            ) : (
                              <div className="mt-1 text-gray-600">No reasons provided.</div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>

                    {crsSummary && (
                      <div>
                        <div className="text-base font-semibold">CRS Breakdown</div>
                        <div className="mt-2 rounded border border-gray-200 bg-gray-50 px-3 py-2 text-sm">
                          <div className="flex items-center justify-between">
                            <span className="font-semibold">CRS Total</span>
                            <span className="text-lg font-bold text-blue-700">{crsSummary.total ?? 0}</span>
                          </div>
                          <div className="mt-2 grid grid-cols-2 gap-2 text-xs text-gray-700 sm:grid-cols-4">
                            {Object.entries(crsSummary.breakdown || {}).map(([key, val]) => (
                              <div key={key} className="rounded bg-white px-2 py-1 shadow-sm">
                                <div className="font-semibold">{key}</div>
                                <div>{val}</div>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    )}

                    {docSummary && (
                      <div className="space-y-3">
                        <div className="text-base font-semibold">Required forms & documents</div>
                        <div className="rounded border border-gray-200 bg-gray-50 px-3 py-2 text-sm">
                          <div className="font-semibold text-gray-800">Forms</div>
                          {docSummary.forms?.length ? (
                            <ul className="mt-1 list-disc pl-5 text-gray-700">
                              {docSummary.forms.map((form) => (
                                <li key={form}>{form}</li>
                              ))}
                            </ul>
                          ) : (
                            <div className="text-gray-600">No forms returned.</div>
                          )}
                        </div>
                        <div className="rounded border border-gray-200 bg-gray-50 px-3 py-2 text-sm">
                          <div className="font-semibold text-gray-800">Documents</div>
                          {docSummary.documents?.length ? (
                            <ul className="mt-1 space-y-1 text-gray-700">
                              {docSummary.documents.map((doc) => (
                                <li key={doc.id} className="rounded bg-white px-2 py-1 shadow-sm">
                                  <div className="font-semibold">{doc.label || doc.id}</div>
                                  <div className="text-xs text-gray-600">
                                    {doc.category ? `Category: ${doc.category}` : "No category"} —{" "}
                                    {doc.mandatory === false ? "Optional" : "Mandatory"}
                                  </div>
                                </li>
                              ))}
                            </ul>
                          ) : (
                            <div className="text-gray-600">No documents returned.</div>
                          )}
                        </div>
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}

