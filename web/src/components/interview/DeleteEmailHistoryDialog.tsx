"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/Button";
import { Dialog } from "@/components/ui/Dialog";
import type {
  EmailHistoryDeleteClassification,
  EmailHistoryEntry,
} from "@/lib/commands/email-commands";

export function DeleteEmailHistoryDialog({
  open,
  entries,
  pending,
  onClose,
  onConfirm,
}: {
  open: boolean;
  entries: EmailHistoryEntry[];
  pending: boolean;
  onClose: () => void;
  onConfirm: (
    classification: EmailHistoryDeleteClassification,
    reason: string | null,
  ) => void;
}) {
  const [classification, setClassification] =
    useState<EmailHistoryDeleteClassification>("WRONG_RECORD");
  const [reason, setReason] = useState("");
  const allTest = entries.length > 0 && entries.every((entry) => entry.environmentCode === "TEST");
  const trimmedReason = reason.trim();
  const valid =
    entries.length > 0 &&
    (classification === "TEST_RECORD"
      ? allTest
      : trimmedReason.length > 0 && trimmedReason.length <= 1000);

  useEffect(() => {
    if (!open) return;
    setClassification(allTest ? "TEST_RECORD" : "WRONG_RECORD");
    setReason("");
  }, [allTest, open]);

  return (
    <Dialog
      open={open}
      title="Xóa Email History"
      onClose={onClose}
      footer={
        <div className="interview-confirm-actions">
          <Button disabled={pending} onClick={onClose}>
            Hủy
          </Button>
          <Button
            variant="danger"
            pending={pending}
            disabled={!valid}
            onClick={() =>
              onConfirm(
                classification,
                classification === "WRONG_RECORD" ? trimmedReason : null,
              )
            }
          >
            Xác nhận xóa
          </Button>
        </div>
      }
    >
      <p>
        Bản ghi vận hành sẽ bị xóa khỏi Email History. Security Audit tương ứng vẫn
        được giữ bất biến.
      </p>
      <p>{entries.length} bản ghi đã chọn.</p>
      <fieldset disabled={pending}>
        <legend>Phân loại xóa</legend>
        <label>
          <input
            type="radio"
            name="email-history-classification"
            value="TEST_RECORD"
            checked={classification === "TEST_RECORD"}
            disabled={!allTest}
            onChange={() => setClassification("TEST_RECORD")}
          />
          TEST_RECORD
        </label>
        {!allTest ? (
          <p className="interview-field-hint">
            TEST_RECORD chỉ dùng khi toàn bộ bản ghi đã chọn thuộc môi trường TEST.
          </p>
        ) : null}
        <label>
          <input
            type="radio"
            name="email-history-classification"
            value="WRONG_RECORD"
            checked={classification === "WRONG_RECORD"}
            onChange={() => setClassification("WRONG_RECORD")}
          />
          WRONG_RECORD
        </label>
      </fieldset>
      {classification === "WRONG_RECORD" ? (
        <label>
          Lý do xóa
          <textarea
            value={reason}
            maxLength={1000}
            rows={4}
            required
            disabled={pending}
            onChange={(event) => setReason(event.target.value)}
          />
          <span className="interview-field-hint">
            {reason.length}/1000 ký tự
          </span>
        </label>
      ) : null}
    </Dialog>
  );
}
