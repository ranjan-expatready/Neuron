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

  it("runs review and renders findings", async () => {
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
        },
        agent_action_id: "action-1",
        agent_session_id: "session-1",
      }),
    });

    render(<DocumentsReviewPage params={{ caseId: "case-1" }} />);

    await waitFor(() => {
      expect(screen.getByText(/Passport/)).toBeInTheDocument();
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
        },
        agent_action_id: "action-2",
        agent_session_id: "session-2",
      }),
    });

    fireEvent.click(screen.getByRole("button", { name: /Run Document Review/i }));

    await waitFor(() => {
      expect(screen.getByText(/ID Card/)).toBeInTheDocument();
    });
  });
});

