import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import React from "react";

jest.mock("next/navigation", () => ({
  useRouter: () => ({ push: jest.fn(), replace: jest.fn() }),
}));

let draftStatus = "draft";

beforeEach(() => {
  draftStatus = "draft";
  global.fetch = jest.fn((url: RequestInfo, opts?: RequestInit) => {
    if (typeof url === "string") {
      if (url.includes("/admin/intake/drafts") && (!opts || opts.method === "GET")) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve([
              {
                id: "d1",
                config_type: "field",
                key: "person.test_field",
                status: draftStatus,
                created_by: "u1",
                updated_by: "u1",
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString(),
                payload: { id: "person.test_field", label: "Test Field" },
              },
            ]),
        } as Response);
      }
      if (url.includes("/submit") && opts && opts.method === "POST") {
        draftStatus = "in_review";
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              id: "d1",
              config_type: "field",
              key: "person.test_field",
              status: "in_review",
              created_by: "u1",
              updated_by: "u1",
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
              payload: { id: "person.test_field", label: "Test Field" },
            }),
        } as Response);
      }
      if (url.includes("/activate") && opts && opts.method === "POST") {
        draftStatus = "active";
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              id: "d1",
              config_type: "field",
              key: "person.test_field",
              status: "active",
              created_by: "u1",
              updated_by: "u1",
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
              approved_by: "admin@example.com",
              approved_at: new Date().toISOString(),
              payload: { id: "person.test_field", label: "Test Field" },
            }),
        } as Response);
      }
      if (url.includes("/reject") && opts && opts.method === "POST") {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              id: "d1",
              config_type: "field",
              key: "person.test_field",
              status: "rejected",
              created_by: "u1",
              updated_by: "u1",
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
              payload: { id: "person.test_field", label: "Test Field" },
            }),
        } as Response);
      }
      if (url.includes("/retire") && opts && opts.method === "POST") {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              id: "d1",
              config_type: "field",
              key: "person.test_field",
              status: "retired",
              created_by: "u1",
              updated_by: "u1",
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
              payload: { id: "person.test_field", label: "Test Field" },
            }),
        } as Response);
      }
      if (url.includes("/admin/intake/drafts") && opts && opts.method === "POST") {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              id: "d2",
              config_type: "field",
              key: "person.new_field",
              status: "draft",
              created_by: "u1",
              updated_by: "u1",
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
              payload: { id: "person.new_field", label: "New Field" },
            }),
        } as Response);
      }
    }
    return Promise.resolve({ ok: false, json: () => Promise.resolve({ detail: "error" }) } as Response);
  }) as any;
});

afterEach(() => {
  jest.resetAllMocks();
});

import DraftsPage from "../src/app/admin/config/intake/drafts/page";

describe("Admin Intake Drafts Page", () => {
  it("renders drafts list and details", async () => {
    render(<DraftsPage />);

    await waitFor(() => {
      expect(screen.getAllByText(/Drafts/i).length).toBeGreaterThan(0);
      expect(screen.getByText(/person.test_field/)).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText(/person.test_field/));
    await waitFor(() => {
      expect(screen.getByText(/Test Field/)).toBeInTheDocument();
    });
  });

  it("allows creating a draft", async () => {
    render(<DraftsPage />);

    await waitFor(() => {
      expect(screen.getAllByText(/Drafts/i).length).toBeGreaterThan(0);
    });

    fireEvent.change(screen.getByPlaceholderText(/e.g., person.test_field/i), {
      target: { value: "person.new_field" },
    });
    fireEvent.change(screen.getByRole("textbox", { name: /Payload/i }), {
      target: { value: '{"id":"person.new_field","label":"New Field","data_path":"profile.personal.x","type":"string"}' },
    });
    fireEvent.click(screen.getByRole("button", { name: /Save Draft/i }));

    await waitFor(() => {
      expect(screen.getByText(/person.new_field/i)).toBeInTheDocument();
    });
  });

  it("supports status actions", async () => {
    render(<DraftsPage />);

    await waitFor(() => {
      expect(screen.getByText(/person.test_field/)).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText(/person.test_field/));

    const submitBtn = screen.getByRole("button", { name: /Submit for review/i });
    fireEvent.click(submitBtn);

    await waitFor(() => expect(global.fetch).toHaveBeenCalledWith(expect.stringContaining("/submit"), expect.anything()));
    await waitFor(() => expect(screen.getAllByText(/in_review/i).length).toBeGreaterThan(0));

    const activateBtn = screen.getByRole("button", { name: /Activate/i });
    fireEvent.click(activateBtn);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining("/activate"),
        expect.objectContaining({ method: "POST" })
      );
    });
  });
});

