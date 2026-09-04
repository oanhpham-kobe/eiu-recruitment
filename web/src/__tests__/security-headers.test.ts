import assert from "node:assert/strict";
import test from "node:test";

import { NextRequest } from "next/server";

import { middleware } from "@/middleware";

test("middleware creates distinct nonces and complete dynamic security headers", () => {
  process.env.NEXT_PUBLIC_SUPABASE_URL = "https://project.supabase.co/rest/v1";

  const firstResponse = middleware(
    new NextRequest("https://app.example.test/"),
  );
  const secondResponse = middleware(
    new NextRequest("https://app.example.test/"),
  );
  const firstNonce = firstResponse.headers.get("x-nonce");
  const secondNonce = secondResponse.headers.get("x-nonce");
  const firstCsp = firstResponse.headers.get("Content-Security-Policy");
  const secondCsp = secondResponse.headers.get("Content-Security-Policy");

  assert.ok(firstNonce);
  assert.ok(secondNonce);
  assert.notEqual(firstNonce, secondNonce);
  assert.match(firstCsp ?? "", new RegExp(`'nonce-${firstNonce}'`));
  assert.match(secondCsp ?? "", new RegExp(`'nonce-${secondNonce}'`));
  assert.match(
    firstCsp ?? "",
    /connect-src 'self' https:\/\/project\.supabase\.co/,
  );
  assert.equal(firstResponse.headers.get("X-Content-Type-Options"), "nosniff");
  assert.equal(
    firstResponse.headers.get("Referrer-Policy"),
    "strict-origin-when-cross-origin",
  );
  assert.equal(
    firstResponse.headers.get("Permissions-Policy"),
    "camera=(), microphone=(), geolocation=()",
  );
  assert.equal(firstResponse.headers.get("X-Frame-Options"), "DENY");
});
