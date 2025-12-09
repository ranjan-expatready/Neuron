"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { apiClient } from "@/lib/api-client";
import Link from "next/link";

interface Case {
  id: string;
  case_number: string;
  case_type: string;
  title: string;
  description: string;
  status: string;
  priority: string;
  notes: string;
  created_at: string;
  updated_at: string;
  submitted_at: string | null;
  decision_date: string | null;
  target_submission_date: string | null;
}

interface Document {
  id: string;
  title: string;
  document_type: string;
  filename: string;
  file_size: number;
  processing_status: string;
  uploaded_at: string;
}

export default function CaseDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();
  const [caseData, setCaseData] = useState<Case | null>(null);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState<
    "overview" | "documents" | "timeline"
  >("overview");

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/auth/login");
    }
  }, [user, authLoading, router]);

  useEffect(() => {
    if (user && params.id) {
      loadCaseData();
      loadDocuments();
    }
  }, [user, params.id]);

  const loadCaseData = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getCase(params.id as string);
      setCaseData(data);
      setError("");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to load case");
    } finally {
      setLoading(false);
    }
  };

  const loadDocuments = async () => {
    try {
      const data = await apiClient.getCaseDocuments(params.id as string);
      setDocuments(data);
    } catch (err: any) {
      console.error("Failed to load documents:", err);
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      draft: "bg-gray-100 text-gray-800",
      active: "bg-blue-100 text-blue-800",
      submitted: "bg-yellow-100 text-yellow-800",
      approved: "bg-green-100 text-green-800",
      rejected: "bg-red-100 text-red-800",
      closed: "bg-gray-100 text-gray-800",
    };
    return colors[status] || "bg-gray-100 text-gray-800";
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i];
  };

  if (authLoading || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!user || !caseData) {
    return null;
  }

  return (
    <div className="min-h-screen bg-secondary-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-secondary-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div>
              <Link
                href="/cases"
                className="text-primary-600 hover:text-primary-900 text-sm mb-2 inline-block"
              >
                ← Back to Cases
              </Link>
              <h1
                className="text-2xl font-bold text-secondary-900"
                data-testid="case-detail-title"
              >
                {caseData.title || "Case Details"}
              </h1>
              <p className="text-sm text-secondary-500">
                Case #{caseData.case_number}
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <span
                className={`px-3 py-1 text-sm font-medium rounded-full ${getStatusColor(
                  caseData.status,
                )}`}
              >
                {caseData.status}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md text-red-800">
            {error}
          </div>
        )}

        {/* Tabs */}
        <div className="mb-6 border-b border-secondary-200">
          <nav className="flex space-x-8">
            <button
              onClick={() => setActiveTab("overview")}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === "overview"
                  ? "border-primary-500 text-primary-600"
                  : "border-transparent text-secondary-500 hover:text-secondary-700 hover:border-secondary-300"
              }`}
            >
              Overview
            </button>
            <button
              onClick={() => setActiveTab("documents")}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === "documents"
                  ? "border-primary-500 text-primary-600"
                  : "border-transparent text-secondary-500 hover:text-secondary-700 hover:border-secondary-300"
              }`}
              data-testid="case-detail-tab-documents"
            >
              Documents ({documents.length})
            </button>
            <button
              onClick={() => setActiveTab("timeline")}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === "timeline"
                  ? "border-primary-500 text-primary-600"
                  : "border-transparent text-secondary-500 hover:text-secondary-700 hover:border-secondary-300"
              }`}
            >
              Timeline
            </button>
          </nav>
        </div>

        {/* Tab Content */}
        {activeTab === "overview" && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Main Info */}
            <div className="lg:col-span-2 space-y-6">
              <div className="card">
                <h2 className="text-lg font-semibold text-secondary-900 mb-4">
                  Case Information
                </h2>
                <dl className="grid grid-cols-1 gap-4">
                  <div>
                    <dt className="text-sm font-medium text-secondary-500">
                      Case Type
                    </dt>
                    <dd className="mt-1 text-sm text-secondary-900">
                      {caseData.case_type}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-secondary-500">
                      Priority
                    </dt>
                    <dd className="mt-1 text-sm text-secondary-900 capitalize">
                      {caseData.priority}
                    </dd>
                  </div>
                  {caseData.description && (
                    <div>
                      <dt className="text-sm font-medium text-secondary-500">
                        Description
                      </dt>
                      <dd className="mt-1 text-sm text-secondary-900">
                        {caseData.description}
                      </dd>
                    </div>
                  )}
                  {caseData.notes && (
                    <div>
                      <dt className="text-sm font-medium text-secondary-500">
                        Notes
                      </dt>
                      <dd className="mt-1 text-sm text-secondary-900 whitespace-pre-wrap">
                        {caseData.notes}
                      </dd>
                    </div>
                  )}
                </dl>
              </div>
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              <div className="card">
                <h2 className="text-lg font-semibold text-secondary-900 mb-4">
                  Key Dates
                </h2>
                <dl className="space-y-3">
                  <div>
                    <dt className="text-xs font-medium text-secondary-500">
                      Created
                    </dt>
                    <dd className="mt-1 text-sm text-secondary-900">
                      {new Date(caseData.created_at).toLocaleDateString()}
                    </dd>
                  </div>
                  {caseData.target_submission_date && (
                    <div>
                      <dt className="text-xs font-medium text-secondary-500">
                        Target Submission
                      </dt>
                      <dd className="mt-1 text-sm text-secondary-900">
                        {new Date(
                          caseData.target_submission_date,
                        ).toLocaleDateString()}
                      </dd>
                    </div>
                  )}
                  {caseData.submitted_at && (
                    <div>
                      <dt className="text-xs font-medium text-secondary-500">
                        Submitted
                      </dt>
                      <dd className="mt-1 text-sm text-secondary-900">
                        {new Date(caseData.submitted_at).toLocaleDateString()}
                      </dd>
                    </div>
                  )}
                  {caseData.decision_date && (
                    <div>
                      <dt className="text-xs font-medium text-secondary-500">
                        Decision Date
                      </dt>
                      <dd className="mt-1 text-sm text-secondary-900">
                        {new Date(caseData.decision_date).toLocaleDateString()}
                      </dd>
                    </div>
                  )}
                </dl>
              </div>

              {/* Progress Tracking */}
              <div className="card">
                <h2 className="text-lg font-semibold text-secondary-900 mb-4">
                  Progress
                </h2>
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-secondary-600">Documents</span>
                    <span className="font-medium">
                      {documents.length} uploaded
                    </span>
                  </div>
                  <div className="w-full bg-secondary-200 rounded-full h-2">
                    <div
                      className="bg-primary-600 h-2 rounded-full"
                      style={{
                        width: `${Math.min(
                          (documents.length / 10) * 100,
                          100,
                        )}%`,
                      }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === "documents" && (
          <div className="card">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-lg font-semibold text-secondary-900">
                Documents
              </h2>
              <Link
                href={`/cases/${params.id}/upload`}
                className="btn btn-primary"
                data-testid="case-detail-upload-link"
              >
                Upload Document
              </Link>
            </div>
            {documents.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-secondary-500 mb-4">
                  No documents uploaded yet
                </p>
                <Link
                  href={`/cases/${params.id}/upload`}
                  className="btn btn-primary"
                  data-testid="case-detail-upload-link-empty"
                >
                  Upload First Document
                </Link>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table
                  className="min-w-full divide-y divide-secondary-200"
                  data-testid="case-documents-table"
                >
                  <thead className="bg-secondary-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase">
                        Title
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase">
                        Type
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase">
                        Size
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase">
                        Uploaded
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-secondary-500 uppercase">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-secondary-200">
                    {documents.map((doc) => (
                      <tr key={doc.id} data-testid="case-documents-row">
                        <td className="px-6 py-4 text-sm text-secondary-900">
                          {doc.title}
                        </td>
                        <td className="px-6 py-4 text-sm text-secondary-500">
                          {doc.document_type}
                        </td>
                        <td className="px-6 py-4 text-sm text-secondary-500">
                          {formatFileSize(doc.file_size)}
                        </td>
                        <td className="px-6 py-4 text-sm">
                          <span
                            className={`px-2 py-1 text-xs font-medium rounded-full ${
                              doc.processing_status === "completed"
                                ? "bg-green-100 text-green-800"
                                : doc.processing_status === "processing"
                                  ? "bg-yellow-100 text-yellow-800"
                                  : "bg-gray-100 text-gray-800"
                            }`}
                          >
                            {doc.processing_status}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-secondary-500">
                          {new Date(doc.uploaded_at).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4 text-right text-sm">
                          <button className="text-primary-600 hover:text-primary-900">
                            View
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {activeTab === "timeline" && (
          <div className="card">
            <h2 className="text-lg font-semibold text-secondary-900 mb-6">
              Case Timeline
            </h2>
            <div className="flow-root">
              <ul className="-mb-8">
                <li>
                  <div className="relative pb-8">
                    <div className="relative flex space-x-3">
                      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary-600">
                        <span className="text-white text-xs">C</span>
                      </div>
                      <div className="flex min-w-0 flex-1 justify-between space-x-4 pt-1.5">
                        <div>
                          <p className="text-sm text-secondary-900">
                            Case created
                          </p>
                        </div>
                        <div className="whitespace-nowrap text-right text-sm text-secondary-500">
                          {new Date(caseData.created_at).toLocaleDateString()}
                        </div>
                      </div>
                    </div>
                  </div>
                </li>
                {caseData.submitted_at && (
                  <li>
                    <div className="relative pb-8">
                      <div className="relative flex space-x-3">
                        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-yellow-600">
                          <span className="text-white text-xs">S</span>
                        </div>
                        <div className="flex min-w-0 flex-1 justify-between space-x-4 pt-1.5">
                          <div>
                            <p className="text-sm text-secondary-900">
                              Case submitted
                            </p>
                          </div>
                          <div className="whitespace-nowrap text-right text-sm text-secondary-500">
                            {new Date(
                              caseData.submitted_at,
                            ).toLocaleDateString()}
                          </div>
                        </div>
                      </div>
                    </div>
                  </li>
                )}
                {caseData.decision_date && (
                  <li>
                    <div className="relative">
                      <div className="relative flex space-x-3">
                        <div
                          className={`flex h-8 w-8 items-center justify-center rounded-full ${
                            caseData.status === "approved"
                              ? "bg-green-600"
                              : "bg-red-600"
                          }`}
                        >
                          <span className="text-white text-xs">D</span>
                        </div>
                        <div className="flex min-w-0 flex-1 justify-between space-x-4 pt-1.5">
                          <div>
                            <p className="text-sm text-secondary-900">
                              Decision: {caseData.status}
                            </p>
                          </div>
                          <div className="whitespace-nowrap text-right text-sm text-secondary-500">
                            {new Date(
                              caseData.decision_date,
                            ).toLocaleDateString()}
                          </div>
                        </div>
                      </div>
                    </div>
                  </li>
                )}
              </ul>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
