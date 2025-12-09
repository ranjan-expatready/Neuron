"use client";

/**
 * Admin Config UI (Read-Only) – Milestone 3.2
 * Plan:
 * - Route: /admin/config (optional ?section=language)
 * - Sidebar lists sections from GET /api/v1/admin/config/sections.
 * - Selecting a section calls GET /api/v1/admin/config/{section} and shows JSON + quick summary.
 * - Banner reminds: read-only, law-sensitive, config-first (no IRCC constants in frontend).
 * - If the API is inaccessible (401/403/network), fall back to a clearly labeled DEV mock sample.
 */

import { useEffect, useMemo, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";

type SectionName = string;

const DEV_MOCK_SECTIONS: SectionName[] = [
  "crs_core",
  "language",
  "program_rules",
  "documents",
  "forms",
];

const DEV_MOCK_DATA: Record<string, unknown> = {
  crs_core: { note: "sample CRS core config (dev mock)" },
  language: { example_minimum: "sample value", clb_tables_ref: "dev-mock" },
  program_rules: {
    programs: [{ code: "FSW", uses_proof_of_funds: true, notes: "sample only" }],
  },
  documents: { documents: { fsw: { base: [{ id: "passport", label: "Passport" }] } } },
  forms: { forms: { express_entry: { fsw: ["IMM0008", "IMM5669"] } } },
};

const bannerClass =
  "rounded-md border border-amber-300 bg-amber-50 text-amber-900 px-4 py-3 text-sm mb-4";

const panelClass = "border rounded-md border-gray-200 bg-white shadow-sm";

export default function AdminConfigPage() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const [sections, setSections] = useState<SectionName[]>([]);
  const [selectedSection, setSelectedSection] = useState<SectionName | undefined>(undefined);
  const [sectionData, setSectionData] = useState<unknown>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [usingMock, setUsingMock] = useState(false);

  const initialSection = searchParams.get("section") || undefined;

  useEffect(() => {
    const fetchSections = async () => {
      setError(null);
      try {
        const res = await fetch("/api/v1/admin/config/sections");
        if (!res.ok) {
          throw new Error(`Sections request failed (${res.status})`);
        }
        const data = (await res.json()) as SectionName[];
        setSections(data);
        const nextSection = initialSection && data.includes(initialSection) ? initialSection : data[0];
        setSelectedSection(nextSection);
        if (nextSection) {
          void fetchSection(nextSection, false);
        }
      } catch (err) {
        console.warn("Admin Config API not accessible, using dev mock:", err);
        setUsingMock(true);
        setSections(DEV_MOCK_SECTIONS);
        const nextSection = initialSection && DEV_MOCK_SECTIONS.includes(initialSection)
          ? initialSection
          : DEV_MOCK_SECTIONS[0];
        setSelectedSection(nextSection);
        if (nextSection) {
          setSectionData(DEV_MOCK_DATA[nextSection]);
        }
        setError("Using dev mock data (API unavailable or unauthorized).");
      }
    };

    const fetchSection = async (section: SectionName, allowMockFallback = true) => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`/api/v1/admin/config/${section}`);
        if (!res.ok) {
          throw new Error(`Section request failed (${res.status})`);
        }
        const data = await res.json();
        setSectionData(data);
        setUsingMock(false);
      } catch (err) {
        console.warn(`Failed to load section ${section}, using mock if allowed:`, err);
        if (allowMockFallback) {
          setUsingMock(true);
          setSectionData(DEV_MOCK_DATA[section] ?? { note: "no mock available for this section" });
          setError("Using dev mock data (API unavailable or unauthorized).");
        } else {
          setError("Unable to load section data.");
        }
      } finally {
        setLoading(false);
      }
    };

    void fetchSections();

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSelect = (section: SectionName) => {
    setSelectedSection(section);
    router.replace(`/admin/config?section=${encodeURIComponent(section)}`);
    if (usingMock) {
      setSectionData(DEV_MOCK_DATA[section] ?? { note: "no mock available for this section" });
      return;
    }
    void (async () => {
      setLoading(true);
      await fetch(`/api/v1/admin/config/${section}`)
        .then(async (res) => {
          if (!res.ok) {
            throw new Error(`Section request failed (${res.status})`);
          }
          const data = await res.json();
          setSectionData(data);
          setError(null);
        })
        .catch((err) => {
          console.warn(`Failed to load section ${section}`, err);
          setError("Unable to load section data; you may need auth. Showing mock if available.");
          setUsingMock(true);
          setSectionData(DEV_MOCK_DATA[section] ?? { note: "no mock available for this section" });
        })
        .finally(() => setLoading(false));
    })();
  };

  const summary = useMemo(() => {
    if (sectionData === null || sectionData === undefined) return "No data loaded";
    if (Array.isArray(sectionData)) return `${sectionData.length} entries`;
    if (typeof sectionData === "object") return `${Object.keys(sectionData as object).length} keys`;
    return typeof sectionData;
  }, [sectionData]);

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <div className="mx-auto max-w-6xl px-4 py-8">
        <div className={bannerClass}>
          <div className="font-semibold">Admin Config – Read-only (Law-sensitive, config-driven)</div>
          <div>Data is loaded from backend Admin Config API. No edits are possible here.</div>
          {usingMock && <div className="mt-1 font-medium text-red-700">Using dev mock sample because the live API was inaccessible.</div>}
        </div>

        <div className="grid grid-cols-12 gap-4">
          <aside className="col-span-12 md:col-span-3">
            <div className={panelClass}>
              <div className="border-b px-4 py-3 font-semibold">Sections</div>
              <div className="max-h-[70vh] overflow-y-auto">
                {sections.length === 0 ? (
                  <div className="px-4 py-3 text-sm text-gray-500">No sections available.</div>
                ) : (
                  <ul className="divide-y">
                    {sections.map((section) => (
                      <li key={section}>
                        <button
                          className={`w-full text-left px-4 py-3 text-sm hover:bg-gray-100 ${
                            section === selectedSection ? "bg-blue-50 text-blue-700 font-semibold" : ""
                          }`}
                          onClick={() => handleSelect(section)}
                        >
                          {section}
                        </button>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
          </aside>

          <main className="col-span-12 md:col-span-9">
            <div className={panelClass}>
              <div className="border-b px-4 py-3">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm text-gray-500">Selected section</div>
                    <div className="text-lg font-semibold">{selectedSection ?? "None"}</div>
                  </div>
                  <div className="text-sm text-gray-500">
                    Summary: <span className="font-medium text-gray-700">{summary}</span>
                  </div>
                </div>
                {error && <div className="mt-2 text-sm text-red-700">{error}</div>}
              </div>
              <div className="p-4">
                {loading ? (
                  <div className="text-sm text-gray-500">Loading...</div>
                ) : sectionData ? (
                  <div className="space-y-3">
                    <div className="text-sm text-gray-600">
                      Data is presented as returned by the Admin Config API (read-only).
                    </div>
                    <pre className="overflow-auto rounded bg-gray-900 p-4 text-xs text-gray-100">
                      {JSON.stringify(sectionData, null, 2)}
                    </pre>
                  </div>
                ) : (
                  <div className="text-sm text-gray-500">Select a section to view its configuration.</div>
                )}
              </div>
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}

