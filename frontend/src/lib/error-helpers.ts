"use client";

import axios, { AxiosError } from "axios";

type DetailValue =
  | string
  | { msg?: string; message?: string }
  | Array<{ msg?: string; message?: string }>
  | unknown;

const normalizeDetail = (detail: DetailValue): string | null => {
  if (!detail) return null;

  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail)) {
    const messages = detail
      .map((entry) => {
        if (typeof entry === "string") {
          return entry;
        }
        if (entry && typeof entry === "object") {
          return entry.msg || entry.message;
        }
        return null;
      })
      .filter(Boolean);

    if (messages.length > 0) {
      return messages.join(", ");
    }
  }

  if (typeof detail === "object") {
    const record = detail as Record<string, unknown>;
    if (typeof record.msg === "string") {
      return record.msg;
    }
    if (typeof record.message === "string") {
      return record.message;
    }
  }

  return null;
};

/**
 * Extracts a user-friendly error message from Axios/JS errors
 */
export const extractApiErrorMessage = (
  error: unknown,
  fallback = "Request failed",
): string => {
  if (!error) {
    return fallback;
  }

  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<any>;
    const detailMessage =
      normalizeDetail(axiosError.response?.data?.detail) ??
      normalizeDetail(axiosError.response?.data) ??
      axiosError.message;

    return detailMessage || fallback;
  }

  if (error instanceof Error) {
    return error.message || fallback;
  }

  if (typeof error === "string") {
    return error;
  }

  return fallback;
};
