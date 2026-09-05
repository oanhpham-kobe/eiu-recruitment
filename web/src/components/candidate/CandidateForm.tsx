"use client";

import type { SupabaseClient } from "@supabase/supabase-js";
import { useState } from "react";
import {
  DocumentUploader,
  type StagedDocumentItem,
} from "@/components/candidate/DocumentUploader";
import { EducationSection } from "@/components/candidate/EducationSection";
import { useAutosave } from "@/hooks/useAutosave";
import type { EducationItem } from "@/lib/commands/candidate-submission";

export interface CandidateFormData {
  fullName: string;
  phone: string;
  dateOfBirth: string;
  gender: string;
  address: string;
  candidateNotes?: string | null;
  education: EducationItem[];
  attachedDocs: StagedDocumentItem[];
  privacyAcknowledged: boolean;
}

interface CandidateFormProps {
  sessionId: string;
  mode: "NEW_SUBMISSION" | "EDIT_SUBMISSION";
  verifiedEmail: string;
  pinnedPrivacyVersion: string;
  initialData?: Partial<CandidateFormData>;
  documentTypes: Array<{ id: string; code: string; name: string }>;
  supabaseClient?: SupabaseClient;
  onSubmit: (
    data: CandidateFormData,
  ) => Promise<{ success: boolean; error?: string }>;
  onCancel: () => Promise<void>;
}

export function CandidateForm({
  sessionId,
  mode,
  verifiedEmail,
  pinnedPrivacyVersion,
  initialData,
  documentTypes,
  supabaseClient,
  onSubmit,
  onCancel,
}: CandidateFormProps) {
  const [formData, setFormData] = useState<CandidateFormData>({
    fullName: initialData?.fullName ?? "",
    phone: initialData?.phone ?? "",
    dateOfBirth: initialData?.dateOfBirth ?? "",
    gender: initialData?.gender ?? "MALE",
    address: initialData?.address ?? "",
    candidateNotes: initialData?.candidateNotes ?? null,
    education: initialData?.education ?? [],
    attachedDocs: initialData?.attachedDocs ?? [],
    privacyAcknowledged: mode === "EDIT_SUBMISSION",
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [serverError, setServerError] = useState<string | null>(null);

  // Autosave hook
  const { statusMessage, clearDraft } = useAutosave({
    sessionId,
    data: formData,
    onRestore: (restored) => {
      // Merge restored draft with verified email
      setFormData((prev) => ({
        ...prev,
        ...restored,
      }));
    },
  });

  const handleFieldChange = (
    field: keyof CandidateFormData,
    value: unknown,
  ) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
    // Clear error for field
    if (errors[field]) {
      setErrors((prev) => {
        const next = { ...prev };
        delete next[field];
        return next;
      });
    }
  };

  const validateForm = (): boolean => {
    const errs: Record<string, string> = {};

    if (!formData.fullName.trim()) {
      errs.fullName = "Họ và tên là bắt buộc / Full name is required";
    }

    if (!formData.phone.trim()) {
      errs.phone = "Số điện thoại là bắt buộc / Phone number is required";
    }

    if (!formData.dateOfBirth) {
      errs.dateOfBirth = "Ngày sinh là bắt buộc / Date of birth is required";
    }

    if (!formData.gender) {
      errs.gender = "Giới tính là bắt buộc / Gender is required";
    }

    if (!formData.address.trim()) {
      errs.address = "Địa chỉ là bắt buộc / Address is required";
    }

    const hasCv = formData.attachedDocs.some(
      (d) => d.isCv || d.documentTypeCode === "CV_RESUME",
    );
    if (!hasCv) {
      errs.attachedDocs = "Bắt buộc phải đính kèm tệp CV / CV is required";
    }

    if (!formData.privacyAcknowledged) {
      errs.privacyAcknowledged =
        "Bạn phải đồng ý với Thông báo quyền riêng tư / You must agree to the Privacy Notice";
    }

    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setServerError(null);

    if (!validateForm()) {
      return;
    }

    setSubmitting(true);
    try {
      const result = await onSubmit(formData);
      if (result.success) {
        clearDraft();
      } else {
        setServerError(
          result.error || "Gửi hồ sơ thất bại / Submission failed",
        );
      }
    } catch (err) {
      setServerError(
        err instanceof Error
          ? err.message
          : "Đã xảy ra lỗi / An error occurred",
      );
    } finally {
      setSubmitting(false);
    }
  };

  const handleCancelClick = async () => {
    clearDraft();
    await onCancel();
  };

  return (
    <form className="candidate-form" onSubmit={handleSubmit} noValidate>
      {serverError && (
        <div
          role="alert"
          style={{
            backgroundColor: "var(--status-danger-bg, #f8e5e0)",
            color: "var(--status-danger-text, #b44425)",
            padding: "12px 16px",
            borderRadius: "6px",
            fontSize: "15px",
            fontWeight: 500,
          }}
        >
          {serverError}
        </div>
      )}

      {/* Section A: Thông tin chung */}
      <fieldset className="form-fieldset">
        <legend className="form-legend">
          A. Thông tin chung / General Information
        </legend>

        <div className="form-grid">
          {/* Full Name */}
          <div className="form-group">
            <label className="form-label" htmlFor="fullName">
              Họ và tên / Full Name <span className="required-mark">*</span>
            </label>
            <input
              id="fullName"
              name="fullName"
              type="text"
              className="form-input"
              value={formData.fullName}
              onChange={(e) => handleFieldChange("fullName", e.target.value)}
              aria-required="true"
              aria-invalid={Boolean(errors.fullName)}
              aria-describedby={errors.fullName ? "fullName-error" : undefined}
              placeholder="Nguyễn Văn A"
              disabled={submitting}
            />
            {errors.fullName && (
              <span id="fullName-error" className="field-error">
                {errors.fullName}
              </span>
            )}
          </div>

          {/* Phone */}
          <div className="form-group">
            <label className="form-label" htmlFor="phone">
              Số điện thoại / Phone <span className="required-mark">*</span>
            </label>
            <input
              id="phone"
              name="phone"
              type="tel"
              className="form-input"
              value={formData.phone}
              onChange={(e) => handleFieldChange("phone", e.target.value)}
              aria-required="true"
              aria-invalid={Boolean(errors.phone)}
              aria-describedby={errors.phone ? "phone-error" : undefined}
              placeholder="0901234567"
              disabled={submitting}
            />
            {errors.phone && (
              <span id="phone-error" className="field-error">
                {errors.phone}
              </span>
            )}
          </div>

          {/* Date of Birth */}
          <div className="form-group">
            <label className="form-label" htmlFor="dateOfBirth">
              Ngày sinh / Date of Birth <span className="required-mark">*</span>
            </label>
            <input
              id="dateOfBirth"
              name="dateOfBirth"
              type="date"
              className="form-input"
              value={formData.dateOfBirth}
              onChange={(e) => handleFieldChange("dateOfBirth", e.target.value)}
              required
              aria-invalid={Boolean(errors.dateOfBirth)}
              aria-describedby={
                errors.dateOfBirth ? "dateOfBirth-error" : undefined
              }
              disabled={submitting}
            />
            {errors.dateOfBirth && (
              <span id="dateOfBirth-error" className="field-error">
                {errors.dateOfBirth}
              </span>
            )}
          </div>

          {/* Gender */}
          <div className="form-group">
            <label className="form-label" htmlFor="gender">
              Giới tính / Gender <span className="required-mark">*</span>
            </label>
            <select
              id="gender"
              name="gender"
              className="form-select"
              value={formData.gender}
              onChange={(e) => handleFieldChange("gender", e.target.value)}
              aria-required="true"
              aria-invalid={Boolean(errors.gender)}
              aria-describedby={errors.gender ? "gender-error" : undefined}
              disabled={submitting}
            >
              <option value="MALE">Nam / Male</option>
              <option value="FEMALE">Nữ / Female</option>
              <option value="OTHER">Khác / Other</option>
            </select>
            {errors.gender && (
              <span id="gender-error" className="field-error">
                {errors.gender}
              </span>
            )}
          </div>

          {/* Email (Readonly) */}
          <div className="form-group">
            <label className="form-label" htmlFor="email">
              Email (Xác thực / Verified)
            </label>
            <input
              id="email"
              name="email"
              type="email"
              className="form-input"
              value={verifiedEmail}
              readOnly
            />
            <span className="file-spec">
              Email xác thực từ phiên đăng nhập, không thể thay đổi.
            </span>
          </div>

          {/* Address */}
          <div className="form-group">
            <label className="form-label" htmlFor="address">
              Địa chỉ hiện tại / Address{" "}
              <span className="required-mark">*</span>
            </label>
            <input
              id="address"
              name="address"
              type="text"
              className="form-input"
              value={formData.address}
              onChange={(e) => handleFieldChange("address", e.target.value)}
              aria-required="true"
              aria-invalid={Boolean(errors.address)}
              aria-describedby={errors.address ? "address-error" : undefined}
              placeholder="Thủ Dầu Một, Bình Dương"
              disabled={submitting}
            />
            {errors.address && (
              <span id="address-error" className="field-error">
                {errors.address}
              </span>
            )}
          </div>
        </div>
      </fieldset>

      {/* Section B: Quá trình học tập */}
      <EducationSection
        items={formData.education}
        onChange={(education) => handleFieldChange("education", education)}
        disabled={submitting}
      />

      {/* Section C: Hồ sơ đính kèm */}
      <DocumentUploader
        sessionId={sessionId}
        attachedDocs={formData.attachedDocs}
        documentTypes={documentTypes}
        onDocsChange={(docs) => handleFieldChange("attachedDocs", docs)}
        supabaseClient={supabaseClient}
        disabled={submitting}
      />
      {errors.attachedDocs && (
        <span className="field-error" style={{ marginTop: "-16px" }}>
          {errors.attachedDocs}
        </span>
      )}

      {/* Section D: Xác nhận quyền riêng tư */}
      <fieldset className="form-fieldset">
        <legend className="form-legend">
          D. Xác nhận quyền riêng tư / Privacy Confirmation{" "}
          <span className="required-mark">*</span>
        </legend>

        <div className="privacy-box">
          <input
            id="privacyAcknowledged"
            type="checkbox"
            className="privacy-checkbox"
            checked={formData.privacyAcknowledged}
            onChange={(e) =>
              handleFieldChange("privacyAcknowledged", e.target.checked)
            }
            aria-required="true"
            aria-invalid={Boolean(errors.privacyAcknowledged)}
            aria-describedby={
              errors.privacyAcknowledged ? "privacy-error" : undefined
            }
            disabled={submitting}
          />
          <label htmlFor="privacyAcknowledged" className="privacy-text">
            Tôi xác nhận đã đọc, hiểu rõ và đồng ý với{" "}
            <strong>
              Thông báo về quyền riêng tư của EIU (Phiên bản{" "}
              {pinnedPrivacyVersion})
            </strong>
            . Dữ liệu của tôi sẽ được lưu trữ và xử lý bảo mật phục vụ công tác
            tuyển dụng.
          </label>
        </div>
        {errors.privacyAcknowledged && (
          <span
            id="privacy-error"
            className="field-error"
            style={{ marginTop: "8px", display: "block" }}
          >
            {errors.privacyAcknowledged}
          </span>
        )}
      </fieldset>

      {/* Footer & Action Bar */}
      <div className="form-footer">
        <div className="autosave-status" role="status" aria-live="polite">
          {statusMessage}
        </div>

        <div className="action-buttons">
          <button
            type="button"
            className="btn btn-secondary"
            onClick={handleCancelClick}
            disabled={submitting}
          >
            Hủy / Cancel
          </button>

          <button
            type="submit"
            className="btn btn-primary"
            disabled={submitting}
          >
            {submitting
              ? "Đang gửi... / Submitting..."
              : mode === "EDIT_SUBMISSION"
                ? "Lưu thay đổi / Save Edit"
                : "Nộp hồ sơ / Submit Application"}
          </button>
        </div>
      </div>
    </form>
  );
}
