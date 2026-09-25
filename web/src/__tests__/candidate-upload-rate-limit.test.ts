import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { NextRequest } from "next/server";
import { POST as completeUpload } from "@/app/api/candidate/uploads/complete/route";
import { POST as reserveUpload } from "@/app/api/candidate/uploads/reserve/route";

function req(pathName: string, body: Record<string, unknown>) {
  return new NextRequest(`https://recruitment.example.test${pathName}`, {
    method: "POST",
    headers: {
      host: "recruitment.example.test",
      origin: "https://recruitment.example.test",
      "content-type": "application/json",
    },
    body: JSON.stringify(body),
  });
}
test("reserve returns 429 and Retry-After", async () => {
  const r = await reserveUpload(
    req("/api/candidate/uploads/reserve", {
      sessionId: "s",
      intendedDocumentTypeId: "d",
      filename: "cv.pdf",
    }),
    undefined,
    {
      resolveTrustedIp: () => "203.0.113.1",
      reserveBoundary: async () => ({
        success: false as const,
        code: "RATE_LIMITED",
        error: "blocked",
        retryAfterSeconds: 41,
      }),
    },
  );
  assert.equal(r.status, 429);
  assert.equal(r.headers.get("Retry-After"), "41");
});
test("complete returns 429 and Retry-After", async () => {
  const r = await completeUpload(
    req("/api/candidate/uploads/complete", {
      sessionId: "s",
      reservationId: "r",
      intendedDocumentTypeId: "d",
      actualSize: 1,
    }),
    undefined,
    {
      resolveTrustedIp: () => "203.0.113.2",
      completeBoundary: async () => ({
        success: false as const,
        code: "RATE_LIMITED",
        error: "blocked",
        retryAfterSeconds: 17,
      }),
    },
  );
  assert.equal(r.status, 429);
  assert.equal(r.headers.get("Retry-After"), "17");
});
test("missing trusted IP fails closed", async () => {
  let calls = 0;
  const r = await reserveUpload(
    req("/api/candidate/uploads/reserve", {
      sessionId: "s",
      intendedDocumentTypeId: "d",
      filename: "cv.pdf",
    }),
    undefined,
    {
      resolveTrustedIp: () => null,
      reserveBoundary: async () => {
        calls += 1;
        throw new Error("no");
      },
    },
  );
  assert.equal(r.status, 503);
  assert.equal(calls, 0);
});
test("UI uses HTTP upload boundaries and CLEAN continuation remains server action", () => {
  const s = fs.readFileSync(
    path.join(process.cwd(), "src/components/candidate/DocumentUploader.tsx"),
    "utf8",
  );
  assert.match(s, /\/api\/candidate\/uploads\/reserve/);
  assert.match(s, /\/api\/candidate\/uploads\/complete/);
  assert.doesNotMatch(s, /reserveUploadAction/);
  assert.doesNotMatch(s, /completeAndStageUploadAction/);
  assert.match(s, /continueCleanDocumentScanAction/);
});
test("legacy Server Actions delegate through trusted IP boundaries", () => {
  const s = fs.readFileSync(
    path.join(process.cwd(), "src/app/candidate/candidate-actions.ts"),
    "utf8",
  );
  assert.match(s, /reserveCandidateUploadBoundary\(input, trustedIp\)/);
  assert.match(s, /completeCandidateUploadBoundary\(input, trustedIp\)/);
});
test("completion limiter precedes inspection and scan", () => {
  const s = fs.readFileSync(
    path.join(process.cwd(), "src/lib/candidate/upload-server.ts"),
    "utf8",
  );
  const g = s.indexOf("authorize_candidate_upload_completion_rate_limited");
  const i = s.indexOf("const inspected = await inspectReservation");
  const q = s.indexOf("request_candidate_document_scan_as_actor");
  assert.ok(g >= 0 && i >= 0 && q >= 0 && g < i && i < q);
});
