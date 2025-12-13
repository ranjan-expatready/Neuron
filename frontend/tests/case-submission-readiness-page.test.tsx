import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import SubmissionReadinessPage from "../src/app/cases/[caseId]/submission-readiness/page";

describe("SubmissionReadinessPage", () => {
  const readinessResponse = {
    status: "READY",
    ready: true,
    missing_documents: [],
    documents: [],
    blockers: [],
    explanations: [],
    engine_version: "1.0.0",
    evaluation_timestamp: "2025-12-13T12:00:00Z",
    config_hash: "abc",
  };

  const evidenceResponse = {
    bundle_version: "v1",
    case_id: "case-1",
    tenant_id: "tenant-1",
    program_code: "EE_FSW",
    engine_version: "1.0.0",
    verification_engine_version: "1.0.0",
    evaluation_timestamp: "2025-12-13T12:00:00Z",
    config_hashes: ["abc"],
    source_bundle_version: "v-source",
    readiness_result: readinessResponse,
    verification_result: {
      verdict: "PASS",
      reasons: [],
      warnings: [],
    },
    evidence_index: ["config/domain/documents.yaml#proof_of_funds"],
  };

  beforeEach(() => {
    jest.resetAllMocks();
  });

  it("renders PASS verdict and audit data", async () => {
    const mockFetch = jest.fn()
      .mockResolvedValueOnce({ ok: true, json: async () => readinessResponse })
      .mockResolvedValueOnce({ ok: true, json: async () => evidenceResponse });
    (global as any).fetch = mockFetch;

    render(<SubmissionReadinessPage params={{ caseId: "case-1" }} />);

    await waitFor(() => {
      expect(screen.getByLabelText("Readiness verification status")).toHaveTextContent("PASS");
    });
    expect(screen.getByText(/Engine versions/i)).toBeInTheDocument();
    expect(screen.getByText(/config\/domain\/documents.yaml/)).toBeInTheDocument();
  });

  it("renders FAIL verdict and blockers", async () => {
    const failReadiness = {
      ...readinessResponse,
      status: "NOT_READY",
      ready: false,
      missing_documents: ["passport_main"],
      documents: [{ id: "passport_main", label: "Passport", category: "identity", unsourced: false }],
      blockers: [{ code: "missing_passport", message: "Passport required", severity: "high" }],
    };
    const failEvidence = {
      ...evidenceResponse,
      readiness_result: failReadiness,
      verification_result: { verdict: "FAIL", reasons: ["blocker_missing_refs"], warnings: [] },
    };

    const mockFetch = jest.fn()
      .mockResolvedValueOnce({ ok: true, json: async () => failReadiness })
      .mockResolvedValueOnce({ ok: true, json: async () => failEvidence });
    (global as any).fetch = mockFetch;

    render(<SubmissionReadinessPage params={{ caseId: "case-2" }} />);

    await waitFor(() => {
      expect(screen.getByLabelText("Readiness verification status")).toHaveTextContent("FAIL");
    });
    expect(screen.getAllByText(/Passport/).length).toBeGreaterThan(0);
    expect(screen.getByText(/missing_passport/)).toBeInTheDocument();
  });

  it("renders UNKNOWN verdict and allows export", async () => {
    const unknownEvidence = {
      ...evidenceResponse,
      verification_result: { verdict: "UNKNOWN", reasons: ["status_unknown"], warnings: [] },
    };
    const mockFetch = jest.fn()
      .mockResolvedValueOnce({ ok: true, json: async () => readinessResponse })
      .mockResolvedValueOnce({ ok: true, json: async () => unknownEvidence });
    (global as any).fetch = mockFetch;

    const createUrl = jest.fn(() => "blob:mock");
    (global as any).URL.createObjectURL = createUrl;
    (global as any).URL.revokeObjectURL = jest.fn();

    render(<SubmissionReadinessPage params={{ caseId: "case-3" }} />);

    await waitFor(() => {
      expect(screen.getByLabelText("Readiness verification status")).toHaveTextContent("UNKNOWN");
    });

    const btn = screen.getByRole("button", { name: /Download Evidence/ });
    fireEvent.click(btn);
    expect(createUrl).toHaveBeenCalled();
  });
});

