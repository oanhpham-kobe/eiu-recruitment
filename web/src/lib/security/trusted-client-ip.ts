import "server-only";

import { isIP } from "node:net";

const VERCEL_TRUSTED_CLIENT_IP_HEADER = "x-vercel-forwarded-for";

export type TrustedClientIpResolverInput = {
  headers: Pick<Headers, "get">;
  isVercel: boolean;
  testTrustedIp?: string;
};

export function normalizeTrustedIp(value: string): string | null {
  const candidate = value.trim();
  if (!candidate || candidate.includes(",")) {
    return null;
  }

  const version = isIP(candidate);
  if (version === 4) {
    return candidate;
  }
  if (version !== 6) {
    return null;
  }

  // WHATWG URL serialization gives one stable compressed representation for a
  // validated IPv6 literal, preventing equivalent spellings from sharding an
  // IP quota. The input was validated before URL parsing and cannot be a host.
  const host = new URL(`http://[${candidate}]/`).hostname;
  return host.startsWith("[") && host.endsWith("]")
    ? host.slice(1, -1).toLowerCase()
    : host.toLowerCase();
}

export function resolveTrustedClientIp(
  input: TrustedClientIpResolverInput,
): string | null {
  if (input.testTrustedIp !== undefined) {
    return normalizeTrustedIp(input.testTrustedIp);
  }

  if (!input.isVercel) {
    // Self-hosted/non-Vercel execution has no approved trusted-proxy contract in
    // the pinned S08-002 baseline. Fail closed rather than trusting forwarding
    // headers merely because a client supplied them.
    return null;
  }

  return normalizeTrustedIp(
    input.headers.get(VERCEL_TRUSTED_CLIENT_IP_HEADER) ?? "",
  );
}

export function resolveTrustedClientIpFromHeaders(
  headers: Pick<Headers, "get">,
): string | null {
  return resolveTrustedClientIp({
    headers,
    isVercel: process.env.VERCEL === "1",
  });
}
