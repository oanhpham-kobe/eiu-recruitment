"use client";

import { useCallback, useEffect, useState } from "react";
import {
  cancelFormSessionAction,
  loadCandidatePortalData,
  startFormSessionAction,
  submitCandidateSubmissionAction,
  updateCandidateSubmissionAction,
} from "@/app/candidate/candidate-actions";
import {
  CandidateForm,
  type CandidateFormData,
} from "@/components/candidate/CandidateForm";
import type { QualificationLevelOption } from "@/components/candidate/EducationSection";
import {
  type CandidateSubmissionSummary,
  SubmissionsList,
} from "@/components/candidate/SubmissionsList";
import "@/styles/candidate-portal.css";

export default function CandidatePortalPage() {
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<
    "NEW_APPLICATION" | "MY_APPLICATIONS"
  >("NEW_APPLICATION");
  const [formMode, setFormMode] = useState<
    "NEW_SUBMISSION" | "EDIT_SUBMISSION"
  >("NEW_SUBMISSION");
  const [sessionId, setSessionId] = useState<string>("");
  const [pinnedPrivacyVersion, setPinnedPrivacyVersion] = useState<string>("");
  const [privacyAlreadyAcknowledged, setPrivacyAlreadyAcknowledged] =
    useState<boolean>(false);
  const [verifiedEmail, setVerifiedEmail] = useState<string>("");
  const [documentTypes, setDocumentTypes] = useState<
    Array<{ id: string; code: string; name: string }>
  >([]);
  const [qualificationLevels, setQualificationLevels] = useState<
    QualificationLevelOption[]
  >([]);
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

  // Initialize or reload real candidate portal data
  const loadPortalData = useCallback(async () => {
    setLoading(true);
    try {
      const res = await loadCandidatePortalData();
      if (res.success) {
        setVerifiedEmail(res.data.verifiedEmail);
        setDocumentTypes(res.data.documentTypes);
        setQualificationLevels(res.data.qualificationLevels);
        setSubmissions(res.data.submissions);

        // If submissions exist and currently on initial load, show MY_APPLICATIONS tab
        if (res.data.submissions.length > 0) {
          setActiveTab("MY_APPLICATIONS");
        } else {
          // No submissions: open a real new form session
          const sessionRes = await startFormSessionAction("NEW_SUBMISSION");
          if (sessionRes.success && sessionRes.data) {
            setSessionId(sessionRes.data.candidate_form_session_id);
            setPinnedPrivacyVersion(
              sessionRes.data.presented_privacy_notice_version ||
                res.data.pinnedPrivacyVersion,
            );
          }
        }
      } else {
        setNotification({
          type: "error",
          message: res.error,
        });
      }
    } catch (err) {
      setNotification({
        type: "error",
        message: err instanceof Error ? err.message : "Lỗi kết nối",
      });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadPortalData();
  }, [loadPortalData]);

  // Start a new form session when switching to NEW_APPLICATION
  const handleStartNewApplication = async () => {
    setLoading(true);
    try {
      const sessionRes = await startFormSessionAction("NEW_SUBMISSION");
      if (sessionRes.success && sessionRes.data) {
        setSessionId(sessionRes.data.candidate_form_session_id);
        setPinnedPrivacyVersion(
          sessionRes.data.presented_privacy_notice_version,
        );
        setPrivacyAlreadyAcknowledged(false);
        setFormMode("NEW_SUBMISSION");
        setEditInitialData(undefined);
        setActiveTab("NEW_APPLICATION");
      } else {
        setNotification({
          type: "error",
          message: sessionRes.error || "Không thể bắt đầu phiên đăng ký",
        });
      }
    } finally {
      setLoading(false);
    }
  };

  const handleFormSubmit = async (
    data: CandidateFormData,
  ): Promise<{ success: boolean; error?: string }> => {
    try {
      if (formMode === "NEW_SUBMISSION") {
        const res = await submitCandidateSubmissionAction({
          candidateFormSessionId: sessionId,
          fullName: data.fullName,
          phone: data.phone,
          dateOfBirth: data.dateOfBirth,
          gender: data.gender,
          address: data.address,
          education: data.education,
          privacyNoticeVersion: pinnedPrivacyVersion,
        });

        if (!res.success) {
          return { success: false, error: res.error };
        }

        setNotification({
          type: "success",
          message:
            "Nộp hồ sơ thành công! / Application submitted successfully.",
        });
      } else {
        const res = await updateCandidateSubmissionAction({
          candidateFormSessionId: sessionId,
          fullName: data.fullName,
          phone: data.phone,
          dateOfBirth: data.dateOfBirth,
          gender: data.gender,
          address: data.address,
          education: data.education,
          privacyNoticeVersion: pinnedPrivacyVersion,
        });

        if (!res.success) {
          return { success: false, error: res.error };
        }

        setNotification({
          type: "success",
          message:
            "Cập nhật hồ sơ thành công! / Application updated successfully.",
        });
      }

      // Refresh persisted state from database
      await loadPortalData();
      setActiveTab("MY_APPLICATIONS");
      setFormMode("NEW_SUBMISSION");
      setEditInitialData(undefined);
      return { success: true };
    } catch (err) {
      return {
        success: false,
        error: err instanceof Error ? err.message : "Submission failed",
      };
    }
  };

  const handleFormCancel = async (): Promise<void> => {
    if (sessionId) {
      await cancelFormSessionAction(sessionId);
    }
    setFormMode("NEW_SUBMISSION");
    setEditInitialData(undefined);
    if (submissions.length > 0) {
      setActiveTab("MY_APPLICATIONS");
    }
  };

  const handleEditSubmission = async (submissionId: string) => {
    const sub = submissions.find((s) => s.submissionId === submissionId);
    if (sub && sub.statusCode === "NEW") {
      setLoading(true);
      try {
        const sessionRes = await startFormSessionAction(
          "EDIT_SUBMISSION",
          submissionId,
        );
        if (sessionRes.success && sessionRes.data) {
          setSessionId(sessionRes.data.candidate_form_session_id);
          setPinnedPrivacyVersion(
            sessionRes.data.presented_privacy_notice_version,
          );
          setPrivacyAlreadyAcknowledged(true);
          setFormMode("EDIT_SUBMISSION");
          setActiveTab("NEW_APPLICATION");
        } else {
          setNotification({
            type: "error",
            message: sessionRes.error || "Không thể mở phiên chỉnh sửa hồ sơ",
          });
        }
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <div className="portal-wrapper">
      <main className="portal-container" id="main-content">
        {/* Header */}
        <header className="portal-header">
          <div className="portal-brand">
            <h1 className="portal-title">Cổng ứng viên / Candidate Portal</h1>
            <p className="portal-subtitle">
              Trường Đại học Quốc tế Miền Đông — Tuyển dụng / EIU Recruitment
            </p>
          </div>

          <div className="portal-user-meta">
            <span className="user-email-label">Ứng viên / Candidate:</span>
            <span className="user-email-value">{verifiedEmail || "..."}</span>
          </div>
        </header>

        {/* Global Notification Banner */}
        {notification && (
          <div
            role="alert"
            className={`portal-alert portal-alert-${notification.type}`}
            aria-live="polite"
          >
            <span>{notification.message}</span>
            <button
              type="button"
              className="alert-dismiss-btn"
              onClick={() => setNotification(null)}
              aria-label="Đóng thông báo / Dismiss notification"
            >
              ✕
            </button>
          </div>
        )}

        {/* Navigation Tabs */}
        <div
          className="portal-tabs"
          role="tablist"
          aria-label="Cổng ứng viên điều hướng"
        >
          <button
            type="button"
            role="tab"
            id="tab-my-apps"
            aria-selected={activeTab === "MY_APPLICATIONS"}
            aria-controls="panel-my-apps"
            className={`portal-tab ${activeTab === "MY_APPLICATIONS" ? "active" : ""}`}
            onClick={() => setActiveTab("MY_APPLICATIONS")}
          >
            Phiếu của tôi / My Applications ({submissions.length})
          </button>

          <button
            type="button"
            role="tab"
            id="tab-new-app"
            aria-selected={activeTab === "NEW_APPLICATION"}
            aria-controls="panel-new-app"
            className={`portal-tab ${activeTab === "NEW_APPLICATION" ? "active" : ""}`}
            onClick={handleStartNewApplication}
          >
            {formMode === "EDIT_SUBMISSION"
              ? "Chỉnh sửa phiếu / Edit Application"
              : "Đăng ký mới / New Application"}
          </button>
        </div>

        {/* Panel 1: My Submissions */}
        <div
          role="tabpanel"
          id="panel-my-apps"
          hidden={activeTab !== "MY_APPLICATIONS"}
        >
          {loading ? (
            <div className="portal-loading-indicator">
              Đang tải... / Loading...
            </div>
          ) : (
            <SubmissionsList
              submissions={submissions}
              onEditSubmission={handleEditSubmission}
              onNewApplication={handleStartNewApplication}
            />
          )}
        </div>

        {/* Panel 2: Registration / Edit Form */}
        <div
          role="tabpanel"
          id="panel-new-app"
          aria-labelledby="tab-new-app"
          hidden={activeTab !== "NEW_APPLICATION"}
        >
          {loading ? (
            <div className="portal-loading-indicator">
              Đang khởi tạo form... / Loading form...
            </div>
          ) : (
            <CandidateForm
              sessionId={sessionId}
              mode={formMode}
              verifiedEmail={verifiedEmail}
              pinnedPrivacyVersion={pinnedPrivacyVersion}
              privacyAlreadyAcknowledged={privacyAlreadyAcknowledged}
              initialData={editInitialData}
              documentTypes={documentTypes}
              qualificationLevels={qualificationLevels}
              onSubmit={handleFormSubmit}
              onCancel={handleFormCancel}
            />
          )}
        </div>
      </main>
    </div>
  );
}
