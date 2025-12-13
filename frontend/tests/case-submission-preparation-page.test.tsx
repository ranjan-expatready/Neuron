import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import SubmissionPreparationPage from "../src/app/cases/[caseId]/submission-preparation/page";

const basePackage = {
  package_version: "v1",
  case_id: "case-1",
  tenant_id: "tenant-1",
  program_code: "EE_FSW",
  engine_versions: ["prep:1.0.0", "readiness:1.0.0", "verification:1.0.0"],
  evaluation_timestamp: "2025-12-13T12:00:00Z",
  forms: [
    {
      form_code: "IMM0008",
      form_name: "Generic App",
      fields: [
        {
          field_code: "given_name",
          source: "canonical_profile",
          value_preview: "John",
          status: "mapped",
          notes: null,
        },
      ],
      attachments: [
        { doc_code: "passport_main", status: "available", evidence_ref: "config/domain/documents.yaml#passport_main" },
      ],
    },
  ],
  gaps_summary: {
    blocking: [],
    non_blocking: [],
  },
  readiness_reference: {
    readiness_verdict: "PASS",
    evidence_bundle_ref: "hash-config",
  },
  audit: {
    config_hashes: ["hash-config"],
    consulted_configs: ["documents.yaml"],
    source_bundle_version: "v-source",
  },
  deterministic_hash: "hash123",
};

describe("SubmissionPreparationPage", () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  it("renders package with no gaps", async () => {
    (global as any).fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => basePackage,
    });

    render(<SubmissionPreparationPage params={{ caseId: "case-1" }} />);

    await screen.findByText(/Blocking gaps: 0/);
    expect(screen.getByText(/given_name/)).toBeInTheDocument();
    expect(screen.getByText(/Hash: hash123/)).toBeInTheDocument();
  });

  it("shows blocking gaps when present", async () => {
    const pkgWithGaps = {
      ...basePackage,
      gaps_summary: { blocking: ["field:IMM0008:given_name"], non_blocking: [] },
    };
    (global as any).fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => pkgWithGaps,
    });

    render(<SubmissionPreparationPage params={{ caseId: "case-2" }} />);

    await waitFor(() => {
      expect(screen.getByText(/Blocking gaps: 1/)).toBeInTheDocument();
      expect(screen.getByText(/field:IMM0008:given_name/)).toBeInTheDocument();
    });
  });

  it("handles UNKNOWN readiness verdict", async () => {
    const pkgUnknown = {
      ...basePackage,
      readiness_reference: { readiness_verdict: "UNKNOWN", evidence_bundle_ref: null },
    };
    (global as any).fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => pkgUnknown,
    });

    render(<SubmissionPreparationPage params={{ caseId: "case-3" }} />);

    await waitFor(() => {
      expect(screen.getByText(/UNKNOWN/)).toBeInTheDocument();
    });
  });

  it("triggers download on export", async () => {
    (global as any).fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => basePackage,
    });

    const createUrl = jest.fn(() => "blob:mock");
    (global as any).URL.createObjectURL = createUrl;
    (global as any).URL.revokeObjectURL = jest.fn();

    render(<SubmissionPreparationPage params={{ caseId: "case-4" }} />);

    const btn = await screen.findByRole("button", { name: /Download preparation package JSON/i });
    fireEvent.click(btn);
    expect(createUrl).toHaveBeenCalled();
  });
});

