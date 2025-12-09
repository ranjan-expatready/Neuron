"use client";

import { useState, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { apiClient } from "@/lib/api-client";
import Link from "next/link";

export default function DocumentUploadPage() {
  const params = useParams();
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();
  const [file, setFile] = useState<File | null>(null);
  const [documentType, setDocumentType] = useState("");
  const [documentCategory, setDocumentCategory] = useState("identity");
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const documentTypes = [
    { value: "passport", label: "Passport", category: "identity" },
    {
      value: "birth_certificate",
      label: "Birth Certificate",
      category: "identity",
    },
    { value: "diploma", label: "Diploma", category: "education" },
    { value: "transcript", label: "Transcript", category: "education" },
    { value: "ielts", label: "IELTS", category: "language" },
    { value: "celpip", label: "CELPIP", category: "language" },
    {
      value: "employment_letter",
      label: "Employment Letter",
      category: "work",
    },
    { value: "pay_stub", label: "Pay Stub", category: "work" },
  ];

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (selectedFile: File) => {
    // Validate file type
    const allowedTypes = [
      ".pdf",
      ".jpg",
      ".jpeg",
      ".png",
      ".doc",
      ".docx",
      ".txt",
    ];
    const fileExt = "." + selectedFile.name.split(".").pop()?.toLowerCase();

    if (!allowedTypes.includes(fileExt)) {
      setError(
        `File type ${fileExt} not allowed. Allowed types: ${allowedTypes.join(
          ", ",
        )}`,
      );
      return;
    }

    // Validate file size (50MB max)
    const maxSize = 50 * 1024 * 1024;
    if (selectedFile.size > maxSize) {
      setError(`File size exceeds 50MB limit`);
      return;
    }

    setFile(selectedFile);
    setError("");

    // Auto-fill title if empty
    if (!title) {
      setTitle(selectedFile.name.replace(/\.[^/.]+$/, ""));
    }
  };

  const handleDocumentTypeChange = (value: string) => {
    setDocumentType(value);
    const matchedType = documentTypes.find((type) => type.value === value);
    setDocumentCategory(matchedType?.category || "other");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!file || !documentType || !title) {
      setError("Please fill in all required fields");
      return;
    }

    setUploading(true);
    setError("");

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("document_type", documentType);
      formData.append("category", documentCategory || "other");
      formData.append("title", title);
      formData.append("description", description || "");
      formData.append("case_id", params.id as string);
      formData.append("access_level", "case_team");

      await apiClient.uploadDocument(formData);

      // Redirect to case detail page
      router.push(`/cases/${params.id}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to upload document");
    } finally {
      setUploading(false);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i];
  };

  if (authLoading) {
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
              <Link
                href={`/cases/${params.id}`}
                className="text-primary-600 hover:text-primary-900 text-sm mb-2 inline-block"
              >
                ← Back to Case
              </Link>
              <h1 className="text-2xl font-bold text-secondary-900">
                Upload Document
              </h1>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* File Upload Area */}
          <div className="card">
            <label className="block text-sm font-medium text-secondary-700 mb-2">
              Document File <span className="text-red-500">*</span>
            </label>

            <div
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                dragActive
                  ? "border-primary-500 bg-primary-50"
                  : file
                    ? "border-green-500 bg-green-50"
                    : "border-secondary-300 hover:border-secondary-400"
              }`}
            >
              {file ? (
                <div className="space-y-2">
                  <svg
                    className="mx-auto h-12 w-12 text-green-500"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                  <p className="text-sm font-medium text-secondary-900">
                    {file.name}
                  </p>
                  <p className="text-xs text-secondary-500">
                    {formatFileSize(file.size)}
                  </p>
                  <button
                    type="button"
                    onClick={() => {
                      setFile(null);
                      if (fileInputRef.current) {
                        fileInputRef.current.value = "";
                      }
                    }}
                    className="text-sm text-red-600 hover:text-red-800"
                  >
                    Remove
                  </button>
                </div>
              ) : (
                <div className="space-y-2">
                  <svg
                    className="mx-auto h-12 w-12 text-secondary-400"
                    stroke="currentColor"
                    fill="none"
                    viewBox="0 0 48 48"
                  >
                    <path
                      d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                      strokeWidth={2}
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                  <div className="text-sm text-secondary-600">
                    <label htmlFor="file-upload" className="cursor-pointer">
                      <span className="text-primary-600 hover:text-primary-500">
                        Click to upload
                      </span>{" "}
                      or drag and drop
                    </label>
                    <input
                      id="file-upload"
                      ref={fileInputRef}
                      type="file"
                      className="sr-only"
                      onChange={handleFileInput}
                      accept=".pdf,.jpg,.jpeg,.png,.doc,.docx,.txt"
                      data-testid="upload-file-input"
                    />
                  </div>
                  <p className="text-xs text-secondary-500">
                    PDF, DOC, DOCX, JPG, PNG, TXT up to 50MB
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Document Type */}
          <div className="card">
            <label
              htmlFor="document_type"
              className="block text-sm font-medium text-secondary-700 mb-2"
            >
              Document Type <span className="text-red-500">*</span>
            </label>
            <select
              id="document_type"
              value={documentType}
              onChange={(e) => handleDocumentTypeChange(e.target.value)}
              required
              className="w-full border border-secondary-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
              data-testid="upload-document-type"
            >
              <option value="">Select document type</option>
              {documentTypes.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          {/* Title */}
          <div className="card">
            <label
              htmlFor="title"
              className="block text-sm font-medium text-secondary-700 mb-2"
            >
              Title <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
              className="w-full border border-secondary-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
              placeholder="Enter document title"
              data-testid="upload-title"
            />
          </div>

          {/* Description */}
          <div className="card">
            <label
              htmlFor="description"
              className="block text-sm font-medium text-secondary-700 mb-2"
            >
              Description
            </label>
            <textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={4}
              className="w-full border border-secondary-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
              placeholder="Optional description"
              data-testid="upload-description"
            />
          </div>

          {/* Error Message */}
          {error && (
            <div
              className="p-4 bg-red-50 border border-red-200 rounded-md text-red-800"
              data-testid="upload-error"
            >
              {error}
            </div>
          )}

          {/* Submit Button */}
          <div className="flex justify-end space-x-4">
            <Link
              href={`/cases/${params.id}`}
              className="btn btn-outline"
              data-testid="upload-cancel"
            >
              Cancel
            </Link>
            <button
              type="submit"
              disabled={uploading || !file || !documentType || !title}
              className="btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
              data-testid="upload-submit"
            >
              {uploading ? "Uploading..." : "Upload Document"}
            </button>
          </div>
        </form>
      </main>
    </div>
  );
}
