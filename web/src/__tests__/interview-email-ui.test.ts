import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import test from "node:test";
import type { EmailHistoryEntry } from "@/lib/commands/email-commands";
import {
  emailHistoryStatusTone,
  emailHistoryTimestamp,
  formatEmailHistoryRecipients,
  validateEmailHistoryDeletion,
} from "@/lib/interview/email-ui";

function source(path: string): string {
  return readFileSync(resolve(process.cwd(), path), "utf8");
}

const baseHistory: EmailHistoryEntry = {
  email_history_id: "10000000-0000-0000-0000-000000000001",
  interview_id: "20000000-0000-0000-0000-000000000001",
  email_type: "INTERVIEW_INVITATION",
  environment_code: "TEST",
  recipients: { to: ["candidate@example.com"], cc: ["audit@example.com"] },
  subject: "Interview invitation",
  template_version: "test-1",
  sent_at: "2026-09-16T10:00:00.000Z",
  created_at: "2026-09-16T09:59:00.000Z",
  status_code: "SENT",
  error_code: null,
};

test("email history UI maps only accepted completed statuses", () => {
  assert.equal(emailHistoryStatusTone("SENT"), "success");
  assert.equal(emailHistoryStatusTone("FAILED"), "danger");
  assert.equal(emailHistoryStatusTone("CANCELLED"), "warning");
  assert.equal(emailHistoryStatusTone("ABANDONED"), "neutral");
});

test("email history UI formats authoritative recipients and timestamps", () => {
  assert.equal(
    formatEmailHistoryRecipients(baseHistory.recipients),
    "candidate@example.com, audit@example.com",
  );
  assert.equal(emailHistoryTimestamp(baseHistory), baseHistory.sent_at);
  assert.equal(
    emailHistoryTimestamp({ ...baseHistory, sent_at: null }),
    baseHistory.created_at,
  );
});

test("delete validation enforces TEST environment and WRONG_RECORD reason", () => {
  assert.equal(validateEmailHistoryDeletion("TEST_RECORD", "", true), null);
  assert.match(
    validateEmailHistoryDeletion("TEST_RECORD", "", false) ?? "",
    /môi trường TEST/i,
  );
  assert.match(
    validateEmailHistoryDeletion("WRONG_RECORD", "   ", false) ?? "",
    /yêu cầu lý do/i,
  );
  assert.equal(
    validateEmailHistoryDeletion("WRONG_RECORD", "Wrong operational record", false),
    null,
  );
  assert.match(
    validateEmailHistoryDeletion("WRONG_RECORD", "x".repeat(1001), false) ?? "",
    /1000/,
  );
});

test("preview UI keeps preview fingerprint fencing and stale-preview refresh without interview status mutation", () => {
  const preview = source("src/components/interview/EmailPreviewDialog.tsx");
  assert.match(preview, /preview_fingerprint: preview\.preview_fingerprint/);
  assert.match(preview, /STALE_PREVIEW/);
  assert.match(preview, /await loadPreview\(/);
  assert.match(preview, /Đã đưa vào hàng đợi|onQueued/);
  assert.doesNotMatch(preview, /changeInterviewStatusAction/);
  assert.doesNotMatch(preview, /schedule_status_code/);
});

test("email actions expose history independently from send permission", () => {
  const actions = source("src/components/interview/InterviewEmailActions.tsx");
  assert.match(actions, /canSend: boolean/);
  assert.match(actions, /canViewHistory: boolean/);
  assert.match(actions, /canDeleteHistory: boolean/);
  assert.match(actions, /!capabilities\.canSend &&\s*!capabilities\.canViewHistory/);
  assert.match(actions, /Lịch sử gửi thư/);
  assert.match(actions, /EmailHistoryDrawer/);
});

test("table-row shortcuts reuse preview-before-send and server-derived recipient authority", () => {
  const rowActions = source("src/components/interview/InterviewRowEmailActions.tsx");
  const page = source("src/components/interview/InterviewPage.tsx");
  assert.match(rowActions, /EmailPreviewDialog/);
  assert.match(rowActions, /INTERVIEW_INVITATION/);
  assert.match(rowActions, /INTERVIEW_PARTICIPANT_INVITATION/);
  assert.match(rowActions, /hasCurrentParticipants/);
  assert.match(rowActions, /application\.candidateEmail/);
  assert.doesNotMatch(rowActions, /participantIds|recipientIds|email_outbox/);
  assert.match(page, /InterviewRowEmailActions/);
  assert.match(page, /application=\{application\}/);
  assert.match(page, /round=\{latest\}/);
  assert.match(page, /round=\{round\}/);
});

test("history drawer stays on email_history projection and renders accessible completed-history controls", () => {
  const history = source("src/components/interview/EmailHistoryDrawer.tsx");
  assert.match(history, /loadInterviewEmailHistoryAction/);
  assert.match(history, /StatusBadge/);
  assert.match(history, /aria-label="Chọn tất cả Email History"/);
  assert.match(history, /<caption className="sr-only">/);
  assert.match(history, /<th scope="col">/);
  assert.match(history, /QUEUED thuộc Email Outbox và không được tổng hợp vào đây/);
  assert.doesNotMatch(history, /from\(["']email_outbox["']\)/);
});

test("history deletion dialog preserves cleanup classification and immutable-audit messaging", () => {
  const deletion = source("src/components/interview/DeleteEmailHistoryDialog.tsx");
  assert.match(deletion, /TEST_RECORD/);
  assert.match(deletion, /WRONG_RECORD/);
  assert.match(deletion, /disabled=!\{?testRecordAllowed\}?|disabled=\{!testRecordAllowed\}/);
  assert.match(deletion, /maxLength=\{1000\}/);
  assert.match(deletion, /required/);
  assert.match(deletion, /security audit.*bất biến/is);
});

test("email UI polish keeps long content scrollable instead of overflowing drawers", () => {
  const css = source("src/components/interview/EmailUi.module.css");
  assert.match(css, /overflow-x:\s*auto/);
  assert.match(css, /white-space:\s*pre-wrap/);
  assert.match(css, /overflow-wrap:\s*anywhere/);
});
