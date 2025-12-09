import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import React from "react";

jest.mock("next/navigation", () => ({
  useSearchParams: () => ({
    get: () => null,
  }),
  useRouter: () => ({
    replace: jest.fn(),
  }),
}));

import Page from "../src/app/express-entry/intake/page";

describe("Express Entry Case Intake UI", () => {
  beforeEach(() => {
    global.fetch = jest.fn((url: RequestInfo) => {
      if (typeof url === "string" && url.endsWith("/api/v1/cases/evaluate")) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              program_eligibility: [
                { program_code: "FSW", eligible: true, reasons: ["meets language"], rule_ids: [] },
              ],
              crs: { total: 450, breakdown: { core_points: 300, additional_points: 50 }, factor_details: [] },
              documents_and_forms: { forms: ["IMM0008"], documents: [{ id: "passport", label: "Passport" }] },
              config_version: {},
              warnings: [],
            }),
        } as Response);
      }
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({}),
      } as Response);
    });
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it("renders form fields and shows results after evaluation", async () => {
    render(<Page />);

    fireEvent.change(screen.getByLabelText(/Age/i), { target: { value: "30" } });
    fireEvent.change(screen.getByLabelText(/Family size/i), { target: { value: "2" } });
    fireEvent.change(screen.getByLabelText(/Highest education/i), { target: { value: "bachelor" } });
    fireEvent.change(screen.getByLabelText(/Test type/i), { target: { value: "IELTS" } });
    fireEvent.change(screen.getByLabelText(/Listening CLB/i), { target: { value: "9" } });
    fireEvent.change(screen.getByLabelText(/Reading CLB/i), { target: { value: "9" } });
    fireEvent.change(screen.getByLabelText(/Writing CLB/i), { target: { value: "9" } });
    fireEvent.change(screen.getByLabelText(/Speaking CLB/i), { target: { value: "9" } });
    fireEvent.change(screen.getByLabelText(/Canadian experience \(years\)/i), { target: { value: "1" } });
    fireEvent.change(screen.getByLabelText(/Foreign experience \(years\)/i), { target: { value: "2" } });
    fireEvent.change(screen.getByLabelText(/Proof of funds \(CAD\)/i), { target: { value: "20000" } });

    fireEvent.click(screen.getByRole("button", { name: /Evaluate my case/i }));

    await waitFor(() => {
      expect(screen.getByText(/Program eligibility/i)).toBeInTheDocument();
      expect(screen.getByText(/FSW/)).toBeInTheDocument();
      expect(screen.getByText(/CRS Total/i)).toBeInTheDocument();
      expect(screen.getByText(/IMM0008/)).toBeInTheDocument();
    });
  });
});


