"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/lib/auth-context";
import { apiClient } from "@/lib/api-client";
import { useRouter } from "next/navigation";
import Link from "next/link";

interface Case {
  id: string;
  case_number: string;
  case_type: string;
  title: string;
  status: string;
  priority: string;
  created_at: string;
  updated_at: string;
}

export default function CasesPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [cases, setCases] = useState<Case[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [page, setPage] = useState(1);
  const pageSize = 20;

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/auth/login");
    }
  }, [user, authLoading, router]);

  useEffect(() => {
    if (user) {
      loadCases();
    }
  }, [user, statusFilter, page]);

  const loadCases = async () => {
    try {
      setLoading(true);
      const params: any = {
        skip: (page - 1) * pageSize,
        limit: pageSize,
      };
      if (statusFilter !== "all") {
        params.status = statusFilter;
      }
      const data = await apiClient.getCases(params);
      setCases(data);
      setError("");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to load cases");
    } finally {
      setLoading(false);
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

  const getPriorityColor = (priority: string) => {
    const colors: Record<string, string> = {
      low: "text-gray-600",
      normal: "text-blue-600",
      high: "text-orange-600",
      urgent: "text-red-600",
    };
    return colors[priority] || "text-gray-600";
  };

  if (authLoading || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-secondary-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-secondary-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div>
              <h1 className="text-2xl font-bold text-secondary-900">Cases</h1>
              <p className="text-sm text-secondary-500">
                Manage your immigration cases
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <Link
                href="/dashboard"
                className="text-secondary-600 hover:text-secondary-900"
              >
                Dashboard
              </Link>
              <Link
                href="/cases/new"
                className="btn btn-primary"
                data-testid="cases-new-case-button"
              >
                New Case
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filters */}
        <div className="mb-6 flex items-center space-x-4">
          <label className="text-sm font-medium text-secondary-700">
            Filter by status:
          </label>
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setPage(1);
            }}
            className="border border-secondary-300 rounded-md px-3 py-2 text-sm"
          >
            <option value="all">All Statuses</option>
            <option value="draft">Draft</option>
            <option value="active">Active</option>
            <option value="submitted">Submitted</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
            <option value="closed">Closed</option>
          </select>
        </div>

        {/* Error Message */}
        {error && (
          <div
            className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md text-red-800"
            data-testid="cases-error"
          >
            {error}
          </div>
        )}

        {/* Cases Table */}
        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table
              className="min-w-full divide-y divide-secondary-200"
              data-testid="cases-table"
            >
              <thead className="bg-secondary-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                    Case Number
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                    Title
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                    Priority
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                    Updated
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-secondary-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-secondary-200">
                {cases.length === 0 ? (
                  <tr>
                    <td
                      colSpan={7}
                      className="px-6 py-8 text-center text-secondary-500"
                    >
                      No cases found.{" "}
                      <Link
                        href="/cases/new"
                        className="text-primary-600 hover:underline"
                      >
                        Create your first case
                      </Link>
                    </td>
                  </tr>
                ) : (
                  cases.map((caseItem) => (
                    <tr
                      key={caseItem.id}
                      className="hover:bg-secondary-50"
                      data-testid="cases-row"
                    >
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-secondary-900">
                        {caseItem.case_number || "N/A"}
                      </td>
                      <td className="px-6 py-4 text-sm text-secondary-900">
                        {caseItem.title || "Untitled Case"}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary-500">
                        {caseItem.case_type}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(
                            caseItem.status,
                          )}`}
                        >
                          {caseItem.status}
                        </span>
                      </td>
                      <td
                        className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${getPriorityColor(
                          caseItem.priority,
                        )}`}
                      >
                        {caseItem.priority}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary-500">
                        {new Date(caseItem.updated_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <Link
                          href={`/cases/${caseItem.id}`}
                          className="text-primary-600 hover:text-primary-900"
                          data-testid="cases-row-view"
                        >
                          View
                        </Link>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {cases.length > 0 && (
            <div className="px-6 py-4 border-t border-secondary-200 flex items-center justify-between">
              <button
                onClick={() => setPage(page - 1)}
                disabled={page === 1}
                className="btn btn-outline disabled:opacity-50"
              >
                Previous
              </button>
              <span className="text-sm text-secondary-600">Page {page}</span>
              <button
                onClick={() => setPage(page + 1)}
                disabled={cases.length < pageSize}
                className="btn btn-outline disabled:opacity-50"
              >
                Next
              </button>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
