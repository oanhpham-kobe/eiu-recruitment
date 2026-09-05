"use client";

import { useEffect, useState } from "react";
import {
  CandidateForm,
  type CandidateFormData,
} from "@/components/candidate/CandidateForm";
import {
  type CandidateSubmissionSummary,
  SubmissionsList,
} from "@/components/candidate/SubmissionsList";
import "@/styles/candidate-portal.css";

const MOCK_DOCUMENT_TYPES = [
  {
    id: "dt-cv-0001-0000-000000000001",
    code: "CV_RESUME",
    name: "CV / Sơ yếu lý lịch",
  },
  {
    id: "dt-deg-0002-0000-000000000002",
    code: "DEGREE",
    name: "Bằng tốt nghiệp",
  },
  {
    id: "dt-tra-0003-0000-000000000003",
    code: "TRANSCRIPT",
    name: "Bảng điểm",
  },
  {
    id: "dt-cer-0004-0000-000000000004",
    code: "CERTIFICATE",
    name: "Chứng chỉ",
  },
  { id: "dt-oth-0005-0000-000000000005", code: "OTHER", name: "Tài liệu khác" },
];

export default function CandidatePortalPage() {
  const [activeTab, setActiveTab] = useState<
    "NEW_APPLICATION" | "MY_APPLICATIONS"
  >("NEW_APPLICATION");
  const [formMode, setFormMode] = useState<
    "NEW_SUBMISSION" | "EDIT_SUBMISSION"
  >("NEW_SUBMISSION");
  const [sessionId, setSessionId] = useState<string>("mock-session-001");
  const [pinnedPrivacyVersion] = useState<string>("2026.1");
  const [verifiedEmail] = useState<string>("candidate@example.com");
  const [submissions, setSubmissions] = useState<CandidateSubmissionSummary[]>(
    [],
  );
  const [editInitialData, setEditInitialData] = useState<
    Partial<CandidateFormData> | undefined
  >(undefined);
  const [notification, setNotification] = useState<{
    type: "success" | "error";
    message: string;
  } | null>(null);

  useEffect(() => {
    // Check if candidate has existing submissions
    if (
      submissions.length > 0 &&
      activeTab === "NEW_APPLICATION" &&
      formMode === "NEW_SUBMISSION"
    ) {
      // Keep active tab as user preference
    }
  }, [submissions.length, activeTab, formMode]);

  const handleFormSubmit = async (
    _data: CandidateFormData,
  ): Promise<{ success: boolean; error?: string }> => {
    try {
      if (formMode === "NEW_SUBMISSION") {
        const newSub: CandidateSubmissionSummary = {
          submissionId: crypto.randomUUID(),
          submittedAt: new Date().toISOString(),
          statusCode: "NEW",
          versionNo: 1,
        };
        setSubmissions((prev) => [newSub, ...prev]);
        setNotification({
          type: "success",
          message:
            "Nộp hồ sơ thành công! / Application submitted successfully.",
        });
        setActiveTab("MY_APPLICATIONS");
      } else {
        // Edit mode: update existing submission
        setSubmissions((prev) =>
          prev.map((sub, idx) =>
            idx === 0
              ? {
                  ...sub,
                  versionNo: sub.versionNo + 1,
                  submittedAt: new Date().toISOString(),
                }
              : sub,
          ),
        );
        setNotification({
          type: "success",
          message:
            "Cập nhật hồ sơ thành công! / Application updated successfully.",
        });
        setActiveTab("MY_APPLICATIONS");
        setFormMode("NEW_SUBMISSION");
        setEditInitialData(undefined);
      }
      return { success: true };
    } catch (err) {
      return {
        success: false,
        error: err instanceof Error ? err.message : "Submission failed",
      };
    }
  };

  const handleFormCancel = async (): Promise<void> => {
    setFormMode("NEW_SUBMISSION");
    setEditInitialData(undefined);
    if (submissions.length > 0) {
      setActiveTab("MY_APPLICATIONS");
    }
  };

  const handleEditSubmission = (submissionId: string) => {
    const sub = submissions.find((s) => s.submissionId === submissionId);
    if (sub && sub.statusCode === "NEW") {
      setFormMode("EDIT_SUBMISSION");
      setSessionId(crypto.randomUUID());
      setEditInitialData({
        fullName: "Nguyễn Văn A",
        phone: "0901234567",
        dateOfBirth: "1995-05-15",
        gender: "MALE",
        address: "Thủ Dầu Một, Bình Dương",
        candidateNotes: "",
      });
      setActiveTab("NEW_APPLICATION");
    }
  };

  return (
    <div className="portal-wrapper">
      <main className="portal-container" id="main-content">
        {/* Header */}
        <header className="portal-header">
          <div className="portal-brand">
            <span className="portal-logo-text">EIU</span>
            <div>
              <h1 style={{ fontSize: "18px", margin: 0, fontWeight: 700 }}>
                Cổng Tuyển Dụng Ứng Viên / Candidate Portal
              </h1>
              <span className="portal-sub">Đại học Quốc tế Miền Đông</span>
            </div>
          </div>

          <div className="portal-user-meta">
            <span className="portal-email-badge">{verifiedEmail}</span>
            <a
              href="/auth/signout"
              className="btn btn-secondary"
              style={{
                minHeight: "36px",
                padding: "4px 12px",
                fontSize: "14px",
              }}
            >
              Đăng xuất / Sign out
            </a>
          </div>
        </header>

        {/* Notification Banner */}
        {notification && (
          <div
            role="status"
            style={{
              padding: "12px 16px",
              borderRadius: "6px",
              marginBottom: "20px",
              backgroundColor:
                notification.type === "success"
                  ? "var(--status-success-bg, #eaf3e6)"
                  : "var(--status-danger-bg, #f8e5e0)",
              color:
                notification.type === "success"
                  ? "var(--status-success-text, #3b6a2a)"
                  : "var(--status-danger-text, #b44425)",
              fontWeight: 600,
            }}
          >
            {notification.message}
          </div>
        )}

        {/* Tab switcher when candidate has submissions or is in edit mode */}
        {(submissions.length > 0 || formMode === "EDIT_SUBMISSION") && (
          <nav className="portal-tabs" aria-label="Điều hướng cổng ứng viên">
            <button
              type="button"
              className="portal-tab-btn"
              role="tab"
              aria-selected={activeTab === "NEW_APPLICATION"}
              onClick={() => {
                setActiveTab("NEW_APPLICATION");
                if (formMode === "EDIT_SUBMISSION") {
                  setFormMode("NEW_SUBMISSION");
                  setEditInitialData(undefined);
                }
              }}
            >
              {formMode === "EDIT_SUBMISSION"
                ? "Chỉnh sửa hồ sơ / Edit Application"
                : "Đăng ký mới / New Application"}
            </button>
            <button
              type="button"
              className="portal-tab-btn"
              role="tab"
              aria-selected={activeTab === "MY_APPLICATIONS"}
              onClick={() => setActiveTab("MY_APPLICATIONS")}
            >
              Phiếu của tôi / My Applications ({submissions.length})
            </button>
          </nav>
        )}

        {/* Tab Content */}
        {activeTab === "NEW_APPLICATION" ? (
          <section aria-labelledby="form-title">
            <h2
              id="form-title"
              style={{
                fontSize: "20px",
                fontWeight: 700,
                marginBottom: "20px",
              }}
            >
              {formMode === "EDIT_SUBMISSION"
                ? "Chỉnh sửa hồ sơ ứng tuyển / Edit Application"
                : "Phiếu đăng ký ứng tuyển / Recruitment Application Form"}
            </h2>
            <CandidateForm
              sessionId={sessionId}
              mode={formMode}
              verifiedEmail={verifiedEmail}
              pinnedPrivacyVersion={pinnedPrivacyVersion}
              initialData={editInitialData}
              documentTypes={MOCK_DOCUMENT_TYPES}
              onSubmit={handleFormSubmit}
              onCancel={handleFormCancel}
            />
          </section>
        ) : (
          <section aria-labelledby="submissions-title">
            <SubmissionsList
              submissions={submissions}
              onEditSubmission={handleEditSubmission}
              onNewApplication={() => {
                setFormMode("NEW_SUBMISSION");
                setEditInitialData(undefined);
                setActiveTab("NEW_APPLICATION");
              }}
            />
          </section>
        )}
      </main>
    </div>
  );
}
