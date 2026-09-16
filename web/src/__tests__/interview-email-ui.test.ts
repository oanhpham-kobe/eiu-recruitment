import assert from "node:assert/strict";
import test from "node:test";
import { build } from "esbuild";
import { type Browser, chromium, type Page } from "playwright";

let cachedScript: string | undefined;
let cachedStyle: string | undefined;

const interviewId = "10000000-0000-0000-0000-000000000001";
const applicationId = "20000000-0000-0000-0000-000000000001";
const submissionId = "30000000-0000-0000-0000-000000000001";
const historyId = "40000000-0000-0000-0000-000000000001";

function previewData(bodyText: string, fingerprint: string, recipients = ["candidate@example.com"]) {
  return {
    success: true,
    data: {
      recipients: { to: recipients, cc: [] },
      subject: "Interview invitation",
      body_text: bodyText,
      template_version: "test-1",
      environment_code: "TEST",
      context_fingerprint: `context-${fingerprint}`,
      preview_fingerprint: fingerprint,
      email_type: "INTERVIEW_INVITATION",
      interview_id: interviewId,
      application_id: applicationId,
      submission_id: submissionId,
    },
  };
}

async function getHarnessBundle(): Promise<{ script: string; style: string }> {
  if (cachedScript && cachedStyle) return { script: cachedScript, style: cachedStyle };

  const bundle = await build({
    absWorkingDir: process.cwd(),
    bundle: true,
    entryPoints: ["src/__tests__/fixtures/interview-email-harness.tsx"],
    format: "iife",
    outdir: "interview-email-fixture",
    platform: "browser",
    conditions: ["browser"],
    write: false,
    plugins: [
      {
        name: "stub-interview-email-server-boundaries",
        setup(b) {
          b.onResolve({ filter: /^server-only$/ }, () => ({
            path: "server-only",
            namespace: "stub-server-only",
          }));
          b.onLoad({ filter: /.*/, namespace: "stub-server-only" }, () => ({
            contents: "module.exports = {};",
          }));
          b.onResolve({ filter: /^@\/app\/interviews\/actions$/ }, () => ({
            path: "interview-actions",
            namespace: "stub-interview-actions",
          }));
          b.onLoad(
            { filter: /.*/, namespace: "stub-interview-actions" },
            () => ({
              contents: `
                function state() {
                  window.__EMAIL_ACTION_DATA__ = window.__EMAIL_ACTION_DATA__ || {};
                  window.__EMAIL_ACTION_LOGS__ = window.__EMAIL_ACTION_LOGS__ || [];
                  return window.__EMAIL_ACTION_DATA__;
                }
                function log(event, payload) {
                  window.__EMAIL_ACTION_LOGS__ = window.__EMAIL_ACTION_LOGS__ || [];
                  window.__EMAIL_ACTION_LOGS__.push({ event, payload });
                }
                function next(name, fallback) {
                  const values = state()[name];
                  return Array.isArray(values) && values.length ? values.shift() : fallback;
                }
                export async function previewInterviewEmailAction(input) {
                  log('preview', input);
                  return next('previewResults', { success: false, error: { code: 'STUB', message: 'preview stub missing' } });
                }
                export async function enqueueInterviewEmailAction(input) {
                  log('enqueue', input);
                  return next('enqueueResults', { success: true, data: { email_outbox_id: '60000000-0000-0000-0000-000000000001' } });
                }
                export async function loadInterviewEmailHistoryAction(input) {
                  log('history', input);
                  return next('historyResults', { success: true, data: [] });
                }
                export async function deleteEmailHistoryEntryAction(input) {
                  log('delete', input);
                  return next('deleteResults', { success: true, data: { email_history_id: input.emailHistoryId } });
                }
              `,
            }),
          );
        },
      },
    ],
  });

  const script = bundle.outputFiles.find((file) => file.path.endsWith(".js"))?.text;
  const style = bundle.outputFiles.find((file) => file.path.endsWith(".css"))?.text;
  if (!script || !style) throw new Error("Interview email fixture did not bundle");
  cachedScript = script;
  cachedStyle = style;
  return { script, style };
}

async function setupPage(
  page: Page,
  style: string,
  script: string,
  data: Record<string, unknown>,
  harness: Record<string, unknown> = {},
) {
  await page.route("http://localhost:3000/**", (route) => {
    route.fulfill({
      status: 200,
      contentType: "text/html",
      body: '<!DOCTYPE html><html><head></head><body><div id="root"></div></body></html>',
    });
  });
  await page.goto("http://localhost:3000");
  await page.evaluate(
    ({ actionData, harnessData }) => {
      (window as unknown as { __EMAIL_ACTION_DATA__: unknown }).__EMAIL_ACTION_DATA__ = actionData;
      (window as unknown as { __EMAIL_ACTION_LOGS__: unknown[] }).__EMAIL_ACTION_LOGS__ = [];
      (window as unknown as { __EMAIL_HARNESS_DATA__: unknown }).__EMAIL_HARNESS_DATA__ = harnessData;
    },
    { actionData: data, harnessData: harness },
  );
  await page.addStyleTag({ content: style });
  await page.addScriptTag({ content: script });
}

test("preview-before-send renders authoritative recipients/subject/body and forwards the retained fingerprint", { timeout: 60_000 }, async () => {
  const { script, style } = await getHarnessBundle();
  let browser: Browser | undefined;
  try {
    browser = await chromium.launch();
    const page = await browser.newPage();
    const pageErrors: string[] = [];
    page.on("pageerror", (error) => pageErrors.push(error.message));

    const body = "Server body line 1\nStart: 2026-09-18\nTopic: Demo";
    await setupPage(page, style, script, {
      previewResults: [previewData(body, "fingerprint-v1")],
      enqueueResults: [
        {
          success: true,
          data: { email_outbox_id: "60000000-0000-0000-0000-000000000001" },
        },
      ],
    });

    await page.getByRole("button", { name: "Open Email Preview" }).click();
    const dialog = page.getByRole("dialog", { name: /Bản xem trước email/i });
    await dialog.waitFor({ state: "visible" });
    assert.match((await dialog.textContent()) ?? "", /candidate@example\.com/);
    assert.match((await dialog.textContent()) ?? "", /Interview invitation/);
    assert.equal(await dialog.locator("pre").textContent(), body);
    assert.equal(await dialog.getByText("Sender", { exact: true }).count(), 0);

    await dialog.getByRole("button", { name: "Xác nhận gửi" }).click();
    await dialog.getByText("Đã đưa vào hàng đợi gửi thư.").waitFor();

    const logs = await page.evaluate(
      () => (window as unknown as { __EMAIL_ACTION_LOGS__: Array<{ event: string; payload: unknown }> }).__EMAIL_ACTION_LOGS__,
    );
    const enqueue = logs.find((entry) => entry.event === "enqueue");
    assert.deepEqual(enqueue?.payload, {
      emailType: "INTERVIEW_INVITATION",
      interviewId,
      applicationId,
      submissionId,
      previewFingerprint: "fingerprint-v1",
      idempotencyKey: (enqueue?.payload as { idempotencyKey: string }).idempotencyKey,
    });
    assert.match(
      (enqueue?.payload as { idempotencyKey: string }).idempotencyKey,
      /^[0-9a-f-]{36}$/i,
    );
    assert.deepEqual(pageErrors, []);
  } finally {
    await browser?.close();
  }
});

test("STALE_PREVIEW refreshes the server preview and keeps the user-facing review notice visible", { timeout: 60_000 }, async () => {
  const { script, style } = await getHarnessBundle();
  let browser: Browser | undefined;
  try {
    browser = await chromium.launch();
    const page = await browser.newPage();
    await setupPage(page, style, script, {
      previewResults: [
        previewData("Old server body", "fingerprint-old"),
        previewData("New server body", "fingerprint-new"),
      ],
      enqueueResults: [
        {
          success: false,
          error: {
            code: "STALE_PREVIEW",
            message: "Thông tin phỏng vấn đã thay đổi, vui lòng xem lại bản xem trước.",
          },
        },
      ],
    });

    await page.getByRole("button", { name: "Open Email Preview" }).click();
    const dialog = page.getByRole("dialog", { name: /Bản xem trước email/i });
    await dialog.getByText("Old server body").waitFor();
    await dialog.getByRole("button", { name: "Xác nhận gửi" }).click();
    await dialog.getByText("New server body").waitFor();
    await dialog
      .getByText("Thông tin phỏng vấn đã thay đổi, vui lòng xem lại bản xem trước.")
      .waitFor();

    const logs = await page.evaluate(
      () => (window as unknown as { __EMAIL_ACTION_LOGS__: Array<{ event: string }> }).__EMAIL_ACTION_LOGS__,
    );
    assert.equal(logs.filter((entry) => entry.event === "preview").length, 2);
  } finally {
    await browser?.close();
  }
});

test("participant invitation preview is server-recipient driven and exposes no participant-subset controls", { timeout: 60_000 }, async () => {
  const { script, style } = await getHarnessBundle();
  let browser: Browser | undefined;
  try {
    browser = await chromium.launch();
    const page = await browser.newPage();
    const participantPreview = previewData(
      "Participant server body",
      "participant-fingerprint",
      ["one@eiu.edu.vn", "two@eiu.edu.vn"],
    );
    participantPreview.data.email_type = "INTERVIEW_PARTICIPANT_INVITATION";
    await setupPage(
      page,
      style,
      script,
      { previewResults: [participantPreview] },
      { emailType: "INTERVIEW_PARTICIPANT_INVITATION" },
    );

    await page.getByRole("button", { name: "Open Email Preview" }).click();
    const dialog = page.getByRole("dialog", { name: /Gửi thư người tham dự/i });
    await dialog.waitFor({ state: "visible" });
    assert.match((await dialog.textContent()) ?? "", /one@eiu\.edu\.vn, two@eiu\.edu\.vn/);
    assert.equal(await dialog.getByRole("checkbox").count(), 0);
  } finally {
    await browser?.close();
  }
});

test("Email History renders settled statuses only and deletion enforces TEST/WRONG classification UX", { timeout: 60_000 }, async () => {
  const { script, style } = await getHarnessBundle();
  let browser: Browser | undefined;
  try {
    browser = await chromium.launch();
    const page = await browser.newPage();
    const base = {
      interviewId,
      emailType: "INTERVIEW_INVITATION",
      recipients: { to: ["candidate@example.com"], cc: [] },
      subject: "Interview",
      templateVersion: "test-1",
      sentAt: null,
      createdAt: "2026-09-16T10:00:00.000Z",
      errorCode: null,
    };
    await setupPage(page, style, script, {
      historyResults: [
        {
          success: true,
          data: [
            {
              ...base,
              emailHistoryId: historyId,
              environmentCode: "PRODUCTION",
              status: "FAILED",
              errorCode: "PROVIDER_REJECTED",
            },
            {
              ...base,
              emailHistoryId: "40000000-0000-0000-0000-000000000002",
              environmentCode: "TEST",
              status: "SENT",
            },
            {
              ...base,
              emailHistoryId: "40000000-0000-0000-0000-000000000003",
              environmentCode: "TEST",
              status: "CANCELLED",
            },
            {
              ...base,
              emailHistoryId: "40000000-0000-0000-0000-000000000004",
              environmentCode: "TEST",
              status: "ABANDONED",
            },
          ],
        },
        { success: true, data: [] },
      ],
      deleteResults: [
        { success: true, data: { email_history_id: historyId } },
      ],
    });

    await page.getByRole("button", { name: "Open Email History" }).click();
    const drawer = page.getByRole("dialog", { name: /Lịch sử gửi thư/i });
    await drawer.waitFor({ state: "visible" });
    for (const status of ["SENT", "FAILED", "CANCELLED", "ABANDONED"]) {
      assert.equal(await drawer.getByText(status, { exact: true }).count(), 1);
    }
    assert.equal(await drawer.getByText("QUEUED", { exact: true }).count(), 0);

    await drawer
      .getByRole("checkbox", { name: `Chọn Email History ${historyId}` })
      .click();
    await drawer.getByRole("button", { name: "Xóa bản ghi đã chọn" }).click();

    const deleteDialog = page.getByRole("dialog", { name: "Xóa Email History" });
    const testRadio = deleteDialog.getByRole("radio", { name: "TEST_RECORD" });
    assert.equal(await testRadio.isDisabled(), true);
    const confirm = deleteDialog.getByRole("button", { name: "Xác nhận xóa" });
    assert.equal(await confirm.isDisabled(), true);
    await deleteDialog.getByLabel("Lý do xóa").fill("Wrong production record");
    assert.equal(await confirm.isDisabled(), false);
    await confirm.click();

    const logs = await page.evaluate(
      () => (window as unknown as { __EMAIL_ACTION_LOGS__: Array<{ event: string; payload: unknown }> }).__EMAIL_ACTION_LOGS__,
    );
    const deletion = logs.find((entry) => entry.event === "delete");
    assert.deepEqual(deletion?.payload, {
      emailHistoryId: historyId,
      classification: "WRONG_RECORD",
      reason: "Wrong production record",
    });
  } finally {
    await browser?.close();
  }
});
