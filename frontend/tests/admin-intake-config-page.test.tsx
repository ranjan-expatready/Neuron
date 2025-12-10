import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import React from "react";

jest.mock("next/navigation", () => ({
  useParams: () => ({}),
  useRouter: () => ({ replace: jest.fn(), push: jest.fn() }),
}));

beforeEach(() => {
  global.fetch = jest.fn((url: RequestInfo) => {
    if (typeof url === "string") {
      if (url.includes("/admin/intake/fields")) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve([
              { id: "person.marital_status", label: "Marital status", data_path: "profile.personal.marital_status", type: "enum" },
            ]),
        } as Response);
      }
      if (url.includes("/admin/intake/templates")) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve([
              {
                id: "tpl1",
                label: "Test Template",
                applicable_programs: ["EE_FSW"],
                applicable_plans: [],
                steps: [{ id: "step1", label: "Step1", fields: [{ id: "person.marital_status", label: "Marital status", data_path: "profile.personal.marital_status", type: "enum" }] }],
              },
            ]),
        } as Response);
      }
      if (url.includes("/admin/intake/documents")) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve([
              { id: "passport_main", label: "Passport", category: "identity", required_for_programs: ["EE_FSW"], required_when: [] },
            ]),
        } as Response);
      }
      if (url.includes("/admin/intake/forms")) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve([
              { id: "imm0008", label: "IMM0008", applicable_programs: ["EE_FSW"], field_mappings: { given_name: "profile.personal.first_name" } },
            ]),
        } as Response);
      }
      if (url.includes("/admin/intake/options")) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ marital_status: [{ value: "single", label: "Single" }] }),
        } as Response);
      }
    }
    return Promise.resolve({ ok: false, json: () => Promise.resolve({}) } as Response);
  }) as any;
});

afterEach(() => {
  jest.resetAllMocks();
});

import Page from "../src/app/admin/config/intake/page";

describe("Admin Intake Config Page", () => {
  it("renders tabs and data for fields/templates/documents/forms", async () => {
    render(<Page />);

    await waitFor(() => {
      expect(screen.getByText(/Admin Intake Config/i)).toBeInTheDocument();
      expect(screen.getAllByText(/Field Dictionary/i).length).toBeGreaterThan(0);
      expect(screen.getByText(/Marital status/i)).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole("button", { name: /Templates/i }));
    await waitFor(() => {
      expect(screen.getByText(/Test Template/i)).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole("button", { name: /Documents/i }));
    await waitFor(() => {
      expect(screen.getAllByText(/Passport/i).length).toBeGreaterThan(0);
    });

    fireEvent.click(screen.getByRole("button", { name: /Forms/i }));
    await waitFor(() => {
      expect(screen.getAllByText(/IMM0008/i).length).toBeGreaterThan(0);
    });
  });
});

