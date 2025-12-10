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
      getCaseProfile: jest.fn(() =>
        Promise.resolve({
          profile: { profile: { personal: { citizenship: "CANADA" } } },
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
                  options_ref: "citizenship_countries",
                  required: true,
                },
              ],
            },
          ],
        }),
      ),
      getIntakeOptions: jest.fn(() =>
        Promise.resolve([
          { value: "CANADA", label: "Canada" },
          { value: "INDIA", label: "India" },
        ]),
      ),
      getDocumentChecklist: jest.fn(() =>
        Promise.resolve([
          { id: "passport_main", label: "Passport", category: "identity", required: true, reasons: ["program_applicable"] },
          { id: "pof", label: "Proof of funds", category: "financial", required: false, reasons: [] },
        ]),
      ),
      getCaseDocuments: jest.fn(() =>
        Promise.resolve([
          { id: "doc-1", document_type: "passport_main", category: "identity", filename: "passport.pdf", original_filename: "passport.pdf" },
        ]),
      ),
      updateCase: jest.fn(() => Promise.resolve({})),
      updateCaseProfile: jest.fn(() => Promise.resolve({ profile: { profile: {} } })),
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
      expect(screen.getAllByText(/Passport/i).length).toBeGreaterThan(0);
      expect(screen.getByText(/Uploaded/i)).toBeInTheDocument();
    });
  });
});

