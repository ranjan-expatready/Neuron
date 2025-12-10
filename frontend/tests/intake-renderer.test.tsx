import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import React from "react";

import { IntakeFormRenderer, IntakeSchema } from "../src/components/IntakeFormRenderer";

const schema: IntakeSchema = {
  program_code: "EE_FSW",
  plan_code: null,
  template_id: "tpl1",
  label: "Test Template",
  steps: [
    {
      id: "step1",
      label: "Step One",
      fields: [
        { id: "person.first_name", label: "First Name", data_path: "profile.personal.first_name", type: "string", ui_control: "text", required: true },
        { id: "person.age", label: "Age", data_path: "profile.personal.age", type: "number", ui_control: "number", validations: { min: 1 } },
        { id: "person.birth_date", label: "Birth Date", data_path: "profile.personal.dob", type: "date", ui_control: "date" },
      ],
    },
    {
      id: "step2",
      label: "Step Two",
      fields: [
        { id: "person.citizenship", label: "Citizenship", data_path: "profile.personal.citizenship", type: "enum", ui_control: "select", options_ref: ["CANADA", "INDIA"], required: true },
        { id: "person.is_married", label: "Married", data_path: "profile.personal.married", type: "boolean", ui_control: "checkbox" },
      ],
    },
  ],
};

describe("IntakeFormRenderer", () => {
  it("renders fields, options, and validates required", async () => {
    const onSubmit = jest.fn();
    const resolveOptionsRef = jest.fn(() =>
      Promise.resolve([
        { value: "CANADA", label: "Canada" },
        { value: "INDIA", label: "India" },
      ]),
    );
    render(
      <IntakeFormRenderer
        schema={schema}
        onSubmit={onSubmit}
        initialValues={{ "person.citizenship": "CANADA" }}
        resolveOptionsRef={resolveOptionsRef}
      />,
    );

    fireEvent.change(screen.getByLabelText(/First Name/i), { target: { value: "" } });
    fireEvent.click(screen.getByRole("button", { name: /Save intake/i }));
    expect(screen.getByText(/required/i)).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText(/First Name/i), { target: { value: "Alice" } });
    fireEvent.change(screen.getByLabelText(/Age/i), { target: { value: "30" } });
    fireEvent.change(screen.getByLabelText(/Birth Date/i), { target: { value: "1995-01-01" } });
    fireEvent.change(screen.getByLabelText(/Citizenship/i), { target: { value: "INDIA" } });
    fireEvent.click(screen.getByLabelText(/Married/i));

    fireEvent.click(screen.getByRole("button", { name: /Save intake/i }));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledTimes(1);
      const payload = onSubmit.mock.calls[0][0];
      expect(payload.profile.personal.first_name).toBe("Alice");
      expect(payload.profile.personal.married).toBe(true);
    });
  });
});

