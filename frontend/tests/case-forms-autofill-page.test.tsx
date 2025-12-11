import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import FormsAutofillPage from "../src/app/cases/[caseId]/forms-autofill/page";

describe("FormsAutofillPage", () => {
  const mockFetch = jest.fn();

  beforeEach(() => {
    (global as any).fetch = mockFetch;
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it("renders preview data and banner", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        bundle_id: "ee_fsw_base_package",
        warnings: [],
        forms: [
          {
            form_id: "IMM0008",
            warnings: [],
            fields: [
              {
                form_id: "IMM0008",
                field_id: "given_name",
                proposed_value: "John",
                source_type: "canonical_profile",
                source_path: "profile.personal.given_name",
                notes: null,
              },
            ],
          },
        ],
      }),
    });

    render(<FormsAutofillPage params={{ caseId: "case-1" }} />);

    await waitFor(() => {
      expect(screen.getByText(/Form Autofill PREVIEW/)).toBeInTheDocument();
      expect(screen.getByText(/IMM0008/)).toBeInTheDocument();
      expect(screen.getAllByText(/given_name/).length).toBeGreaterThan(0);
      expect(screen.getByText(/canonical_profile/)).toBeInTheDocument();
      expect(screen.getByText(/John/)).toBeInTheDocument();
    });

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        bundle_id: "ee_fsw_base_package",
        warnings: ["No mappings found for form TEST"],
        forms: [],
      }),
    });

    fireEvent.click(screen.getByRole("button", { name: /Refresh Preview/i }));

    await waitFor(() => {
      expect(screen.getByText(/No forms available/)).toBeInTheDocument();
      expect(screen.getByText(/No mappings found/)).toBeInTheDocument();
    });
  });
});

