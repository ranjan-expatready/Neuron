/**
 * API Client for backend communication
 */
import axios, { AxiosInstance } from "axios";
import Cookies from "js-cookie";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        "Content-Type": "application/json",
      },
    });

    // Add request interceptor to include auth token
    this.client.interceptors.request.use((config) => {
      const token = Cookies.get("auth_token");
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Handle unauthorized - clear token and redirect
          Cookies.remove("auth_token");
          if (typeof window !== "undefined") {
            window.location.href = "/auth/login";
          }
        }
        return Promise.reject(error);
      },
    );
  }

  // Cases API
  async getCases(params?: {
    skip?: number;
    limit?: number;
    status?: string;
    case_type?: string;
  }) {
    const response = await this.client.get("/api/v1/cases/", { params });
    return response.data;
  }

  async getCase(caseId: string) {
    const response = await this.client.get(`/api/v1/cases/${caseId}`);
    return response.data;
  }

  async createCase(data: any) {
    const response = await this.client.post("/api/v1/cases/", data);
    return response.data;
  }

  async updateCase(caseId: string, data: any) {
    const response = await this.client.put(`/api/v1/cases/${caseId}`, data);
    return response.data;
  }

  async deleteCase(caseId: string) {
    const response = await this.client.delete(`/api/v1/cases/${caseId}`);
    return response.data;
  }

  async getCaseStatistics() {
    const response = await this.client.get("/api/v1/cases/stats/summary");
    return response.data;
  }

  // Documents API
  async uploadDocument(formData: FormData) {
    const response = await this.client.post(
      "/api/v1/documents/upload",
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      },
    );
    return response.data;
  }

  async getDocuments(params?: {
    case_id?: string;
    person_id?: string;
    document_type?: string;
  }) {
    const response = await this.client.get("/api/v1/documents/", { params });
    return response.data;
  }

  async getDocument(documentId: string) {
    const response = await this.client.get(`/api/v1/documents/${documentId}`);
    return response.data;
  }

  async updateDocument(documentId: string, data: any) {
    const response = await this.client.put(
      `/api/v1/documents/${documentId}`,
      data,
    );
    return response.data;
  }

  async deleteDocument(documentId: string) {
    const response = await this.client.delete(
      `/api/v1/documents/${documentId}`,
    );
    return response.data;
  }

  async getCaseDocuments(caseId: string) {
    const response = await this.client.get(`/api/v1/documents/case/${caseId}`);
    return response.data;
  }

  // Persons API
  async createPerson(data: any) {
    const response = await this.client.post("/api/v1/persons/", data);
    return response.data;
  }
}

export const apiClient = new ApiClient();
