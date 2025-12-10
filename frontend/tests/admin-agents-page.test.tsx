import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import React from "react";

jest.mock("next/navigation", () => ({
  useRouter: () => ({ push: jest.fn(), replace: jest.fn() }),
}));

beforeEach(() => {
  global.fetch = jest.fn((url: RequestInfo, opts?: RequestInit) => {
    if (typeof url === "string" && url.includes("/admin/agents/client-engagement/settings")) {
      return Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            auto_intake_reminders_enabled: false,
            auto_missing_docs_reminders_enabled: false,
            min_days_between_intake_reminders: 7,
            min_days_between_docs_reminders: 7,
          }),
      } as Response);
    }
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
    if (typeof url === "string" && url.includes("/admin/agents/actions")) {
      return Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve([
            {
              id: "a1",
              agent_name: "client_engagement",
              action_type: "suggest_intake_reminder",
              status: "suggested",
              auto_mode: false,
              case_id: "case-123",
              created_at: new Date().toISOString(),
              payload: { message: "Reminder" },
            },
          ]),
      } as Response);
    }
    return Promise.resolve({ ok: false, json: () => Promise.resolve({ detail: "error" }) } as Response);
  }) as any;
});

afterEach(() => {
  jest.resetAllMocks();
});

import AdminAgentsPage from "../src/app/admin/agents/page";

describe("Admin Agents Page", () => {
  it("renders agent actions and details", async () => {
    render(<AdminAgentsPage />);

    await waitFor(() => {
      expect(screen.getByText(/client_engagement/)).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText(/client_engagement/));

    await waitFor(() => {
      expect(screen.getAllByText(/suggest_intake_reminder/).length).toBeGreaterThan(0);
      expect(screen.getAllByText(/case-123/).length).toBeGreaterThan(0);
    });
  });

  it("filters by agent name", async () => {
    render(<AdminAgentsPage />);

    fireEvent.change(screen.getByPlaceholderText(/e.g., client_engagement/i), { target: { value: "client_engagement" } });

    await waitFor(() => {
      const calls = (global.fetch as jest.Mock).mock.calls;
      expect(calls.some((call) => String(call[0]).includes("agent_name=client_engagement"))).toBe(true);
    });
  });

  it("saves settings and triggers auto run", async () => {
    render(<AdminAgentsPage />);
    await waitFor(() => expect(screen.getByText(/Save settings/i)).toBeInTheDocument());

    fireEvent.click(screen.getByText(/Save settings/i));
    await waitFor(() => expect((global.fetch as jest.Mock).mock.calls.some((c) => String(c[0]).includes("/settings"))).toBe(true));

    fireEvent.click(screen.getByText(/Run AUTO for this tenant now/i));
    await waitFor(() => expect(screen.getByText(/Processed 1 cases/i)).toBeInTheDocument());
  });
});

