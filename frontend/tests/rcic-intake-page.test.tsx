import { render, screen, waitFor } from "@testing-library/react";
import React from "react";

jest.mock("next/navigation", () => ({
  useParams: () => ({ caseId: "case-123" }),
}));

jest.mock("../src/lib/api-client", () => {
  return {
    apiClient: {
      getCase: jest.fn(() =>
        Promise.resolve({
          id: "case-123",
          case_metadata: { program_code: "EE_FSW" },
          form_data: { profile: { personal: { citizenship: "CANADA" } } },
        }),
      ),
      getIntakeSchema: jest.fn(() =>
        Promise.resolve({
          program_code: "EE_FSW",
          plan_code: null,
          template_id: "tpl1",
          label: "Test Template",
          steps: [
            {
              id: "step1",
              label: "Personal",
              fields: [
                {
                  id: "person.citizenship",
                  label: "Citizenship",
                  data_path: "profile.personal.citizenship",
                  type: "enum",
                  ui_control: "select",
                  options_ref: ["CANADA", "INDIA"],
                  required: true,
                },
              ],
            },
          ],
        }),
      ),
      getDocumentChecklist: jest.fn(() =>
        Promise.resolve([
          { id: "passport_main", label: "Passport", category: "identity", required: true, reasons: ["program_applicable"] },
          { id: "pof", label: "Proof of funds", category: "financial", required: false, reasons: [] },
        ]),
      ),
      updateCase: jest.fn(() => Promise.resolve({})),
    },
  };
});

import Page from "../src/app/cases/[caseId]/intake/page";

describe("RCIC Intake Page", () => {
  it("renders schema-driven intake and checklist", async () => {
    render(<Page />);

    await waitFor(() => {
      expect(screen.getByText(/Schema-driven intake/i)).toBeInTheDocument();
      expect(screen.getByText(/Citizenship/i)).toBeInTheDocument();
      expect(screen.getByText(/Required documents/i)).toBeInTheDocument();
      expect(screen.getByText(/Passport/i)).toBeInTheDocument();
    });
  });
});

