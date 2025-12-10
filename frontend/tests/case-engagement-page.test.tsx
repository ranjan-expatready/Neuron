import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import React from "react";

jest.mock("next/navigation", () => ({
  useRouter: () => ({ push: jest.fn(), replace: jest.fn() }),
}));

const mockSuggestion = {
  suggestion: {
    message_type: "intake_incomplete_reminder",
    subject: "Draft: Intake completion reminder",
    body: "Please complete your intake",
    requires_approval: true,
    llm_used: true,
  },
  action_id: "action-1",
};

beforeEach(() => {
  global.fetch = jest.fn((url: RequestInfo, opts?: RequestInit) => {
    if (typeof url === "string" && url.includes("client-engagement/auto-run")) {
      return Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            cases_processed: 1,
            intake_reminders: 1,
            docs_reminders: 0,
            details: [],
          }),
      } as Response);
    }
    if (typeof url === "string" && url.includes("client-engagement/intake-reminder")) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockSuggestion),
      } as Response);
    }
    if (typeof url === "string" && url.includes("client-engagement/missing-docs-reminder")) {
      return Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            suggestion: { message_type: "missing_documents_reminder", body: "Docs missing", requires_approval: true },
            action_id: "action-2",
          }),
      } as Response);
    }
    if (typeof url === "string" && url.includes("client-engagement/client-question-reply")) {
      return Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            suggestion: { message_type: "client_question_reply", body: "Draft reply", requires_approval: true },
            action_id: "action-3",
          }),
      } as Response);
    }
    return Promise.resolve({ ok: false, text: () => Promise.resolve("error") } as Response);
  }) as any;
});

afterEach(() => {
  jest.resetAllMocks();
});

import CaseEngagementPage from "../src/app/cases/[caseId]/engagement/page";

describe("Case Engagement Page", () => {
  it("generates intake reminder suggestion", async () => {
    render(<CaseEngagementPage params={{ caseId: "case-123" }} />);

    fireEvent.click(screen.getByText(/Intake incomplete reminder/i));

    await waitFor(() => {
      expect(screen.getByText(/Draft: Intake completion reminder/i)).toBeInTheDocument();
      expect(screen.getByText(/Generated with AI/i)).toBeInTheDocument();
    });
  });

  it("requires question text for question reply", async () => {
    render(<CaseEngagementPage params={{ caseId: "case-123" }} />);

    fireEvent.click(screen.getByText(/Draft reply to client question/i));
    await waitFor(() => {
      expect(screen.getByText(/enter a client question/i)).toBeInTheDocument();
    });
  });

  it("runs auto for case", async () => {
    render(<CaseEngagementPage params={{ caseId: "case-123" }} />);
    fireEvent.click(screen.getByText(/Run AUTO engagement for this case/i));
    await waitFor(() => {
      expect(screen.getByText(/Auto run: intake reminders 1/i)).toBeInTheDocument();
    });
  });
});

