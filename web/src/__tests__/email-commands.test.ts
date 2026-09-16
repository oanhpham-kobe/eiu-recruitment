import assert from "node:assert/strict";
import test from "node:test";
import type { SupabaseClient } from "@supabase/supabase-js";
import {
  bulkEnqueueInterviewEmails,
  deleteEmailHistoryEntry,
  enqueueInterviewEmail,
  loadInterviewEmailHistory,
  previewInterviewEmail,
  type InterviewEmailRequest,
} from "@/lib/commands/email-commands";

const interviewId = "10000000-0000-0000-0000-000000000001";
const applicationId = "20000000-0000-0000-0000-000000000001";
const submissionId = "30000000-0000-0000-0000-000000000001";
const historyId = "40000000-0000-0000-0000-000000000001";
const idempotencyKey = "50000000-0000-0000-0000-000000000001";
const previewFingerprint = "preview-fingerprint-1";

interface MockOptions {
  permissions?: string[];
  authenticated?: boolean;
  rpc?: Record<string, (args: unknown) => unknown>;
  historyRows?: Array<Record<string, unknown>>;
}

function createMockSupabase(options: MockOptions = {}) {
  const rpcCalls: Array<{ fn: string; args: unknown }> = [];
  const fromCalls: Array<{ table: string; op: string; value?: unknown }> = [];
  const permissions = options.permissions ?? [
    "interviews.email",
    "emails.history_view",
    "emails.history_delete",
  ];

  const historyQuery = {
    select(value: string) {
      fromCalls.push({ table: "email_history", op: "select", value });
      return this;
    },
    eq(column: string, value: unknown) {
      fromCalls.push({ table: "email_history", op: `eq:${column}`, value });
      return this;
    },
    in(column: string, value: unknown) {
      fromCalls.push({ table: "email_history", op: `in:${column}`, value });
      return this;
    },
    order(column: string, value: unknown) {
      fromCalls.push({ table: "email_history", op: `order:${column}`, value });
      return Promise.resolve({ data: options.historyRows ?? [], error: null });
    },
  };

  const client = {
    auth: {
      getUser: async () =>
        options.authenticated === false
          ? { data: { user: null }, error: null }
          : {
              data: {
                user: {
                  id: "a0000000-0000-0000-0000-000000000001",
                  email: "hr@eiu.edu.vn",
                },
              },
              error: null,
            },
    },
    rpc: async (fn: string, args?: unknown) => {
      rpcCalls.push({ fn, args });
      if (fn === "get_current_internal_session") {
        return {
          data: {
            success: true,
            data: {
              app_user_id: "b0000000-0000-0000-0000-000000000001",
              is_active: true,
              is_root_admin: false,
              roles: ["HR"],
              permissions,
            },
          },
          error: null,
        };
      }
      return {
        data: options.rpc?.[fn]?.(args) ?? null,
        error: null,
      };
    },
    from: (table: string) => {
      fromCalls.push({ table, op: "from" });
      if (table !== "email_history") throw new Error(`Unexpected table ${table}`);
      return historyQuery;
    },
  } as unknown as SupabaseClient;

  return { client, rpcCalls, fromCalls };
}

function targetCalls(calls: Array<{ fn: string; args: unknown }>) {
  return calls.filter((call) => call.fn !== "get_current_internal_session");
}

test("previewInterviewEmail forwards exactly the accepted four RPC parameters and returns preview_fingerprint", async () => {
  const preview = {
    recipients: { to: ["candidate@example.com"], cc: [] },
    subject: "Interview",
    body_text: "Non-production recruitment notification.\nStart: 2026-09-17",
    template_version: "test-1",
    environment_code: "TEST",
    context_fingerprint: "context-fp",
    preview_fingerprint: previewFingerprint,
    email_type: "INTERVIEW_INVITATION",
    interview_id: interviewId,
    application_id: applicationId,
    submission_id: submissionId,
  };
  const mock = createMockSupabase({
    rpc: {
      preview_email: () => ({ success: true, data: preview }),
    },
  });

  const result = await previewInterviewEmail(
    {
      emailType: "INTERVIEW_INVITATION",
      interviewId,
      applicationId,
      submissionId,
    },
    mock.client,
  );

  assert.equal(result.success, true);
  if (result.success) {
    assert.equal(result.data.preview_fingerprint, previewFingerprint);
    assert.deepEqual(result.data.recipients, {
      to: ["candidate@example.com"],
      cc: [],
    });
  }
  assert.deepEqual(targetCalls(mock.rpcCalls), [
    {
      fn: "preview_email",
      args: {
        p_email_type: "INTERVIEW_INVITATION",
        p_interview_id: interviewId,
        p_application_id: applicationId,
        p_submission_id: submissionId,
      },
    },
  ]);
});

test("enqueueInterviewEmail sends the exact five-key preview-fenced request and idempotency key", async () => {
  const mock = createMockSupabase({
    rpc: {
      enqueue_email: () => ({
        success: true,
        data: { email_outbox_id: "60000000-0000-0000-0000-000000000001" },
      }),
    },
  });

  const result = await enqueueInterviewEmail(
    {
      emailType: "INTERVIEW_INVITATION",
      interviewId,
      applicationId,
      submissionId,
      previewFingerprint,
    },
    idempotencyKey,
    mock.client,
  );

  assert.equal(result.success, true);
  const calls = targetCalls(mock.rpcCalls);
  assert.equal(calls.length, 1);
  assert.equal(calls[0]?.fn, "enqueue_email");
  assert.deepEqual(calls[0]?.args, {
    p_request: {
      email_type: "INTERVIEW_INVITATION",
      interview_id: interviewId,
      application_id: applicationId,
      submission_id: submissionId,
      preview_fingerprint: previewFingerprint,
    },
    p_idempotency_key: idempotencyKey,
  });
  assert.deepEqual(
    Object.keys((calls[0]?.args as { p_request: object }).p_request).sort(),
    [
      "application_id",
      "email_type",
      "interview_id",
      "preview_fingerprint",
      "submission_id",
    ],
  );
});

test("enqueueInterviewEmail preserves backend STALE_PREVIEW and FORBIDDEN instead of inventing success or QUEUED", async () => {
  for (const errorCode of ["STALE_PREVIEW", "FORBIDDEN"]) {
    const mock = createMockSupabase({
      rpc: {
        enqueue_email: () => ({ success: false, error_code: errorCode }),
      },
    });
    const result = await enqueueInterviewEmail(
      {
        emailType: "INTERVIEW_PARTICIPANT_INVITATION",
        interviewId,
        applicationId,
        submissionId,
        previewFingerprint,
      },
      idempotencyKey,
      mock.client,
    );
    assert.equal(result.success, false);
    if (!result.success) assert.equal(result.error.code, errorCode);
  }
});

test("bulkEnqueueInterviewEmails forwards 1..100 complete requests and maps per-item success/failed arrays", async () => {
  const request: InterviewEmailRequest = {
    email_type: "INTERVIEW_PARTICIPANT_INVITATION",
    interview_id: interviewId,
    application_id: applicationId,
    submission_id: submissionId,
    preview_fingerprint: previewFingerprint,
  };
  const mock = createMockSupabase({
    rpc: {
      bulk_enqueue_email: () => ({
        success: [
          {
            id: interviewId,
            email_type: request.email_type,
            application_id: applicationId,
            submission_id: submissionId,
            email_outbox_id: "60000000-0000-0000-0000-000000000001",
          },
        ],
        failed: [],
      }),
    },
  });

  const result = await bulkEnqueueInterviewEmails(
    [request],
    idempotencyKey,
    mock.client,
  );

  assert.equal(result.success, true);
  if (result.success) {
    assert.equal(result.data.success.length, 1);
    assert.equal(result.data.failed.length, 0);
  }
  assert.deepEqual(targetCalls(mock.rpcCalls), [
    {
      fn: "bulk_enqueue_email",
      args: { p_requests: [request], p_idempotency_key: idempotencyKey },
    },
  ]);

  const empty = await bulkEnqueueInterviewEmails([], idempotencyKey, mock.client);
  assert.equal(empty.success, false);
  if (!empty.success) assert.equal(empty.error.code, "VALIDATION_ERROR");
});

test("loadInterviewEmailHistory scopes to interview history and only accepts settled history statuses", async () => {
  const mock = createMockSupabase({
    historyRows: [
      {
        email_history_id: historyId,
        interview_id: interviewId,
        email_type: "INTERVIEW_INVITATION",
        environment_code: "TEST",
        recipients: { to: ["candidate@example.com"], cc: [] },
        subject: "Interview",
        template_version: "test-1",
        sent_at: null,
        created_at: "2026-09-16T10:00:00.000Z",
        status_code: "FAILED",
        error_code: "PROVIDER_REJECTED",
      },
      {
        email_history_id: "40000000-0000-0000-0000-000000000002",
        interview_id: interviewId,
        email_type: "INTERVIEW_INVITATION",
        environment_code: "TEST",
        recipients: { to: ["candidate@example.com"], cc: [] },
        subject: "Should be dropped",
        template_version: "test-1",
        sent_at: null,
        created_at: "2026-09-16T10:00:00.000Z",
        status_code: "QUEUED",
        error_code: null,
      },
    ],
  });

  const result = await loadInterviewEmailHistory(interviewId, mock.client);

  assert.equal(result.success, true);
  if (result.success) {
    assert.deepEqual(result.data.map((entry) => entry.status), ["FAILED"]);
  }
  assert.equal(mock.fromCalls.some((call) => call.table === "email_outbox"), false);
  assert.deepEqual(
    mock.fromCalls.find((call) => call.op === "eq:interview_id")?.value,
    interviewId,
  );
  assert.deepEqual(
    mock.fromCalls.find((call) => call.op === "in:status_code")?.value,
    ["SENT", "FAILED", "CANCELLED", "ABANDONED"],
  );
});

test("deleteEmailHistoryEntry validates cleanup classification/reason and forwards the trusted delete RPC", async () => {
  const mock = createMockSupabase({
    rpc: {
      delete_email_history: () => ({
        success: true,
        data: { email_history_id: historyId },
      }),
    },
  });

  const invalidWrong = await deleteEmailHistoryEntry(
    historyId,
    "WRONG_RECORD",
    "   ",
    mock.client,
  );
  assert.equal(invalidWrong.success, false);
  assert.equal(targetCalls(mock.rpcCalls).length, 0);

  const result = await deleteEmailHistoryEntry(
    historyId,
    "WRONG_RECORD",
    "  duplicate operational record  ",
    mock.client,
  );
  assert.equal(result.success, true);
  const calls = targetCalls(mock.rpcCalls);
  assert.deepEqual(calls, [
    {
      fn: "delete_email_history",
      args: {
        p_email_history_id: historyId,
        p_classification: "WRONG_RECORD",
        p_reason: "duplicate operational record",
      },
    },
  ]);
});

test("adapter may present missing-session UX as UNAUTHENTICATED but never calls or rewrites the backend RPC", async () => {
  const mock = createMockSupabase({ authenticated: false });
  const result = await previewInterviewEmail(
    {
      emailType: "INTERVIEW_INVITATION",
      interviewId,
      applicationId,
      submissionId,
    },
    mock.client,
  );

  assert.equal(result.success, false);
  if (!result.success) assert.equal(result.error.code, "UNAUTHENTICATED");
  assert.deepEqual(targetCalls(mock.rpcCalls), []);
});
