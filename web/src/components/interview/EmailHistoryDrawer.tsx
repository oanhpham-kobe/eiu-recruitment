"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import {
  deleteEmailHistoryEntryAction,
  loadInterviewEmailHistoryAction,
} from "@/app/interviews/actions";
import { Button } from "@/components/ui/Button";
import { Drawer } from "@/components/ui/Drawer";
import { StatusBadge } from "@/components/ui/StatusBadge";
import type {
  EmailHistoryDeleteClassification,
  EmailHistoryEntry,
  EmailHistoryStatus,
} from "@/lib/commands/email-commands";
import { DeleteEmailHistoryDialog } from "./DeleteEmailHistoryDialog";

function statusTone(status: EmailHistoryStatus) {
  if (status === "SENT") return "success" as const;
  if (status === "FAILED") return "danger" as const;
  if (status === "CANCELLED") return "warning" as const;
  return "neutral" as const;
}

function formatTimestamp(value: string | null): string {
  if (!value) return "—";
  return new Intl.DateTimeFormat("vi-VN", {
    timeZone: "Asia/Ho_Chi_Minh",
    dateStyle: "short",
    timeStyle: "short",
  }).format(new Date(value));
}

export function EmailHistoryDrawer({
  open,
  interviewId,
  canDelete,
  onClose,
}: {
  open: boolean;
  interviewId: string;
  canDelete: boolean;
  onClose: () => void;
}) {
  const [entries, setEntries] = useState<EmailHistoryEntry[]>([]);
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [pending, setPending] = useState(false);
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);

  const load = useCallback(async () => {
    setPending(true);
    setFeedback(null);
    const result = await loadInterviewEmailHistoryAction(interviewId);
    if (result.success) {
      setEntries(result.data);
      setSelected(new Set());
    } else {
      setEntries([]);
      setFeedback(result.error.message);
    }
    setPending(false);
  }, [interviewId]);

  useEffect(() => {
    if (!open) return;
    void load();
  }, [load, open]);

  const selectedEntries = useMemo(
    () => entries.filter((entry) => selected.has(entry.emailHistoryId)),
    [entries, selected],
  );

  const confirmDelete = async (
    classification: EmailHistoryDeleteClassification,
    reason: string | null,
  ) => {
    if (!selectedEntries.length) return;
    setPending(true);
    setFeedback(null);
    for (const entry of selectedEntries) {
      const result = await deleteEmailHistoryEntryAction({
        emailHistoryId: entry.emailHistoryId,
        classification,
        reason,
      });
      if (!result.success) {
        setFeedback(result.error.message);
        setPending(false);
        return;
      }
    }
    setDeleteOpen(false);
    await load();
  };

  return (
    <>
      <Drawer
        open={open}
        title="Lịch sử gửi thư / Email History"
        onClose={onClose}
        footer={
          canDelete ? (
            <div className="interview-drawer-actions">
              <Button
                variant="danger"
                disabled={pending || selected.size === 0}
                onClick={() => setDeleteOpen(true)}
              >
                Xóa bản ghi đã chọn
              </Button>
            </div>
          ) : undefined
        }
      >
        {pending && !entries.length ? <p role="status">Đang tải Email History…</p> : null}
        {feedback ? (
          <div className="ui-alert ui-alert--error" role="alert">
            {feedback}
          </div>
        ) : null}
        {!pending && !entries.length && !feedback ? (
          <p>Chưa có lần gửi đã hoàn tất hoặc được worker xử lý cho Interview này.</p>
        ) : null}
        {entries.length ? (
          <div className="interview-email-history-table-wrap">
            <table className="interview-email-history-table">
              <thead>
                <tr>
                  {canDelete ? <th scope="col">Chọn</th> : null}
                  <th scope="col">Người nhận</th>
                  <th scope="col">Subject</th>
                  <th scope="col">Loại</th>
                  <th scope="col">Trạng thái</th>
                  <th scope="col">Thời gian</th>
                  <th scope="col">Lỗi</th>
                </tr>
              </thead>
              <tbody>
                {entries.map((entry) => (
                  <tr key={entry.emailHistoryId}>
                    {canDelete ? (
                      <td>
                        <input
                          type="checkbox"
                          aria-label={`Chọn Email History ${entry.emailHistoryId}`}
                          checked={selected.has(entry.emailHistoryId)}
                          disabled={pending}
                          onChange={(event) => {
                            setSelected((current) => {
                              const next = new Set(current);
                              if (event.target.checked) next.add(entry.emailHistoryId);
                              else next.delete(entry.emailHistoryId);
                              return next;
                            });
                          }}
                        />
                      </td>
                    ) : null}
                    <td>{entry.recipients.to.join(", ") || "—"}</td>
                    <td>{entry.subject ?? "—"}</td>
                    <td>{entry.emailType}</td>
                    <td>
                      <StatusBadge tone={statusTone(entry.status)}>
                        {entry.status}
                      </StatusBadge>
                    </td>
                    <td>{formatTimestamp(entry.sentAt ?? entry.createdAt)}</td>
                    <td>{entry.errorCode ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : null}
      </Drawer>
      <DeleteEmailHistoryDialog
        open={deleteOpen}
        entries={selectedEntries}
        pending={pending}
        onClose={() => setDeleteOpen(false)}
        onConfirm={(classification, reason) =>
          void confirmDelete(classification, reason)
        }
      />
    </>
  );
}
