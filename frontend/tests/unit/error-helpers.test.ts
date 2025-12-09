import { AxiosError } from "axios";
import { describe, expect, it } from "vitest";
import { extractApiErrorMessage } from "@/lib/error-helpers";

const createAxiosError = (detail: any, message = "Request failed") =>
  new AxiosError(message, "ERR_BAD_REQUEST", {}, {}, {
    data: detail,
    status: 400,
    statusText: "Bad Request",
    headers: {},
    config: {},
  } as any);

describe("extractApiErrorMessage", () => {
  it("returns string details from Axios error", () => {
    const error = createAxiosError({ detail: "Invalid credentials" });
    expect(extractApiErrorMessage(error)).toBe("Invalid credentials");
  });

  it("returns joined details from array", () => {
    const detail = {
      detail: [{ msg: "Email required" }, { msg: "Password required" }],
    };
    const error = createAxiosError(detail);
    expect(extractApiErrorMessage(error)).toBe(
      "Email required, Password required",
    );
  });

  it("falls back to response data string", () => {
    const error = createAxiosError("Backend unavailable");
    expect(extractApiErrorMessage(error)).toBe("Backend unavailable");
  });

  it("uses Error message for non-Axios errors", () => {
    const error = new Error("Something broke");
    expect(extractApiErrorMessage(error)).toBe("Something broke");
  });

  it("returns fallback when no detail available", () => {
    const error = createAxiosError({}, "");
    expect(extractApiErrorMessage(error, "Custom fallback")).toBe(
      "Custom fallback",
    );
  });
});
