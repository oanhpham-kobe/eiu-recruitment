"use client";

import type { SupabaseClient } from "@supabase/supabase-js";
import { useState } from "react";
import {
  APPROVED_FILE_EXTENSIONS,
  CANDIDATE_QUARANTINE_BUCKET,
  CANDIDATE_QUARANTINE_FILE_SIZE_LIMIT,
  extractExtension,
  isApprovedExtension,
} from "@/lib/storage/buckets";

export type StagedDocumentItem = {
  changeId?: string;
  reservationId: string;
  documentTypeCode:
    | "CV_RESUME"
    | "DEGREE"
    | "TRANSCRIPT"
    | "CERTIFICATE"
    | "OTHER"
    | string;
  documentTypeName: string;
  filename: string;
  fileSizeBytes: number;
  isCv: boolean;
};

interface DocumentUploaderProps {
  sessionId: string;
  attachedDocs: StagedDocumentItem[];
  documentTypes: Array<{ id: string; code: string; name: string }>;
  onDocsChange: (docs: StagedDocumentItem[]) => void;
  supabaseClient?: SupabaseClient;
  disabled?: boolean;
}

export function DocumentUploader({
  sessionId,
  attachedDocs,
  documentTypes,
  onDocsChange,
  supabaseClient,
  disabled = false,
}: DocumentUploaderProps) {
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploading, setUploading] = useState<boolean>(false);
  const [selectedType, setSelectedType] = useState<string>(
    documentTypes.find((d) => d.code === "CV_RESUME")?.id ||
      documentTypes[0]?.id ||
      "",
  );

  const hasCv = attachedDocs.some(
    (d) => d.isCv || d.documentTypeCode === "CV_RESUME",
  );
  const isMaxReached = attachedDocs.length >= 5;

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploadError(null);

    if (isMaxReached) {
      setUploadError(
        "Hồ sơ chỉ được phép đính kèm tối đa 5 tài liệu / Max 5 documents allowed",
      );
      e.target.value = "";
      return;
    }

    if (file.size > CANDIDATE_QUARANTINE_FILE_SIZE_LIMIT) {
      setUploadError(
        "Dung lượng tệp vượt quá giới hạn 5 MB / File size exceeds 5 MB",
      );
      e.target.value = "";
      return;
    }

    const ext = extractExtension(file.name);
    if (!ext || !isApprovedExtension(ext)) {
      setUploadError(
        `Định dạng tệp không được hỗ trợ. Định dạng hợp lệ: ${APPROVED_FILE_EXTENSIONS.join(", ")}`,
      );
      e.target.value = "";
      return;
    }

    const docType = documentTypes.find((d) => d.id === selectedType);
    if (!docType) {
      setUploadError(
        "Vui lòng chọn loại tài liệu / Please select a document type",
      );
      e.target.value = "";
      return;
    }

    setUploading(true);

    try {
      // In web app, reservation, upload, and completion execute through Supabase / server actions
      // For simulated / client component context:
      const reservationId = crypto.randomUUID();
      const tempPath = `temp/${sessionId}/${reservationId}/${file.name.replace(/[^a-zA-Z0-9._-]/g, "_")}`;

      if (supabaseClient) {
        // Direct storage upload to private quarantine bucket
        const { error: storageError } = await supabaseClient.storage
          .from(CANDIDATE_QUARANTINE_BUCKET)
          .upload(tempPath, file, { upsert: false });

        if (storageError) {
          throw new Error(`Upload failed: ${storageError.message}`);
        }
      }

      const newDoc: StagedDocumentItem = {
        changeId: crypto.randomUUID(),
        reservationId,
        documentTypeCode: docType.code,
        documentTypeName: docType.name,
        filename: file.name,
        fileSizeBytes: file.size,
        isCv: docType.code === "CV_RESUME",
      };

      onDocsChange([...attachedDocs, newDoc]);
      e.target.value = "";
    } catch (err) {
      setUploadError(
        err instanceof Error ? err.message : "Tải tệp thất bại / Upload failed",
      );
    } finally {
      setUploading(false);
    }
  };

  const handleRemove = (index: number) => {
    const updated = attachedDocs.filter((_, idx) => idx !== index);
    onDocsChange(updated);
  };

  const formatSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <fieldset className="form-fieldset">
      <legend className="form-legend">
        Hồ sơ đính kèm / Document Attachments{" "}
        <span className="required-mark">*</span>
      </legend>

      <p className="file-spec" style={{ marginBottom: "16px" }}>
        Định dạng hỗ trợ: PDF, DOC, DOCX, PPT, PPTX, PNG, JPG. Tối đa 5 MB/tệp.
        Tối đa 5 tài liệu. Bắt buộc phải có <strong>CV / Sơ yếu lý lịch</strong>
        .
      </p>

      {/* CV Requirement Warning if missing */}
      {!hasCv && (
        <div
          role="alert"
          style={{
            backgroundColor: "var(--status-warning-bg, #fff0de)",
            color: "var(--status-warning-text, #8a4f00)",
            padding: "10px 14px",
            borderRadius: "6px",
            marginBottom: "16px",
            fontSize: "14px",
            fontWeight: 600,
          }}
        >
          ⚠️ Bắt buộc đính kèm ít nhất 1 tệp CV / Resume trước khi nộp hồ sơ.
        </div>
      )}

      {/* Error Message */}
      {uploadError && (
        <div
          role="alert"
          style={{
            backgroundColor: "var(--status-danger-bg, #f8e5e0)",
            color: "var(--status-danger-text, #b44425)",
            padding: "10px 14px",
            borderRadius: "6px",
            marginBottom: "16px",
            fontSize: "14px",
          }}
        >
          {uploadError}
        </div>
      )}

      {/* Upload Controls */}
      <div className="form-grid" style={{ marginBottom: "20px" }}>
        <div className="form-group">
          <label className="form-label" htmlFor="doc-type-select">
            Loại tài liệu / Document Type
          </label>
          <select
            id="doc-type-select"
            className="form-select"
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            disabled={disabled || isMaxReached || uploading}
          >
            {documentTypes.map((dt) => (
              <option key={dt.id} value={dt.id}>
                {dt.name}{" "}
                {dt.code === "CV_RESUME" ? "(Bắt buộc)" : "(Tùy chọn)"}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="file-input">
            Chọn tệp tải lên / Select File
          </label>
          <input
            id="file-input"
            type="file"
            className="form-input"
            accept=".pdf,.doc,.docx,.ppt,.pptx,.png,.jpg,.jpeg"
            onChange={handleFileSelect}
            disabled={disabled || isMaxReached || uploading}
            style={{ paddingTop: "6px" }}
          />
        </div>
      </div>

      {uploading && (
        <p className="file-spec">Đang xử lý tải lên... / Uploading...</p>
      )}

      {/* Attached Files List */}
      <div className="uploader-box">
        {attachedDocs.map((doc, idx) => (
          <div key={doc.reservationId} className="upload-card attached">
            <div className="upload-meta">
              <div>
                <strong>{doc.documentTypeName}</strong>: {doc.filename} (
                {formatSize(doc.fileSizeBytes)})
                {doc.isCv && (
                  <span
                    style={{
                      marginLeft: "8px",
                      fontSize: "12px",
                      backgroundColor: "var(--status-info-bg, #e5edf5)",
                      color: "var(--eiu-blue, #144069)",
                      padding: "2px 6px",
                      borderRadius: "4px",
                    }}
                  >
                    CV Bắt buộc
                  </span>
                )}
              </div>
              <button
                type="button"
                className="btn btn-danger"
                style={{ minHeight: "36px", padding: "4px 12px" }}
                onClick={() => handleRemove(idx)}
                disabled={disabled}
                aria-label={`Xóa tệp ${doc.filename}`}
              >
                Gỡ bỏ / Remove
              </button>
            </div>
          </div>
        ))}
      </div>
    </fieldset>
  );
}
