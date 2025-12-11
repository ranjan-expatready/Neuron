import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import DocumentsReviewPage from "../src/app/cases/[caseId]/documents-review/page";

describe("DocumentsReviewPage", () => {
  const mockFetch = jest.fn();

  beforeEach(() => {
    (global as any).fetch = mockFetch;
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it("runs review and renders findings with warnings", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        program_code: "EE_FSW",
        case_id: "case-1",
        findings: {
          required_present: [{ requirement_id: "passport", label: "Passport", filenames: ["p1.pdf"] }],
          required_missing: [],
          optional_present: [],
          duplicates: [],
          unmatched: [],
          content_warnings: [{ issue: "empty_or_unreadable", document_id: "d1" }],
          quality_warnings: [],
          heuristic_findings: [
            { finding_code: "passport.missing_keywords", severity: "warning", details: { missing_keywords: ["surname"] } },
          ],
        },
        agent_action_id: "action-1",
        agent_session_id: "session-1",
      }),
    });

    render(<DocumentsReviewPage params={{ caseId: "case-1" }} />);

    await waitFor(() => {
      expect(screen.getByText(/Passport/)).toBeInTheDocument();
      expect(screen.getAllByText(/empty_or_unreadable/).length).toBeGreaterThan(0);
      expect(screen.getAllByText(/Heuristic Findings/)[0]).toBeInTheDocument();
      expect(screen.getAllByText(/missing_keywords/).length).toBeGreaterThan(0);
    });

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        program_code: "EE_FSW",
        case_id: "case-1",
        findings: {
          required_present: [],
          required_missing: [{ requirement_id: "id_card", label: "ID Card", filenames: [] }],
          optional_present: [],
          duplicates: [],
          unmatched: [],
          content_warnings: [{ issue: "unexpected_file_extension", extension: ".txt" }],
          quality_warnings: [],
          heuristic_findings: [],
        },
        agent_action_id: "action-2",
        agent_session_id: "session-2",
      }),
    });

    fireEvent.click(screen.getByRole("button", { name: /Run Document Review/i }));

    await waitFor(() => {
      expect(screen.getByText(/ID Card/)).toBeInTheDocument();
      expect(screen.getAllByText(/unexpected_file_extension/).length).toBeGreaterThan(0);
    });
  });
});

