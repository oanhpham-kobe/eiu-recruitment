import "server-only";

import { createHash } from "node:crypto";
import {
  RATE_LIMIT_POLICIES,
  type RateLimitPolicyCode,
  type RateLimitPrincipalKind,
} from "@/lib/security/rate-limit-policy";
import { createAdminClient } from "@/lib/supabase/admin";

export const RATE_LIMITED_CODE = "RATE_LIMITED" as const;
export const RATE_LIMIT_UNAVAILABLE_CODE = "RATE_LIMIT_UNAVAILABLE" as const;

export type RateLimitContext = {
  email?: string;
  identity?: string;
  trustedIp?: string;
  candidateId?: string;
  actorId?: string;
  emailType?: string;
  entityId?: string;
};

export type DurableRateLimitRule = {
  ruleCode: string;
  keyDigest: string;
  limit: number;
  windowSeconds: number;
};

type RpcResult = {
  data: unknown;
  error: { message: string } | null;
};

export type RateLimitRpcClient = {
  rpc: (
    name: string,
    args: Record<string, unknown>,
  ) => PromiseLike<RpcResult>;
};

export type RateLimitAllowedDecision = {
  allowed: true;
  policyCode: RateLimitPolicyCode;
  rules: Array<{
    ruleCode: string;
    limit: number;
    windowSeconds: number;
    remaining: number;
    resetAt: string;
  }>;
};

export type RateLimitDeniedDecision = {
  allowed: false;
  code: typeof RATE_LIMITED_CODE;
  policyCode: RateLimitPolicyCode;
  retryAfterSeconds: number;
  blockedRules: Array<{
    ruleCode: string;
    limit: number;
    windowSeconds: number;
    retryAfterSeconds: number;
    resetAt: string;
  }>;
};

export type RateLimitUnavailableDecision = {
  allowed: false;
  code: typeof RATE_LIMIT_UNAVAILABLE_CODE;
  policyCode: RateLimitPolicyCode;
};

export type RateLimitDecision =
  | RateLimitAllowedDecision
  | RateLimitDeniedDecision
  | RateLimitUnavailableDecision;

function requireValue(value: string | undefined, label: string): string {
  const normalized = value?.trim();
  if (!normalized) {
    throw new Error(`Missing rate limit ${label} context`);
  }
  return normalized;
}

function normalizeEmail(value: string): string {
  return value.trim().toLowerCase();
}

function normalizeOpaqueIdentity(value: string): string {
  return value.trim().toLowerCase();
}

function composite(...values: string[]): string {
  return values.join("\u001f");
}

function resolvePrincipal(
  principal: RateLimitPrincipalKind,
  context: RateLimitContext,
): string {
  switch (principal) {
    case "EMAIL":
      return normalizeEmail(requireValue(context.email, "email"));
    case "IDENTITY":
      return normalizeOpaqueIdentity(requireValue(context.identity, "identity"));
    case "TRUSTED_IP":
      return requireValue(context.trustedIp, "trusted IP");
    case "CANDIDATE":
      return normalizeOpaqueIdentity(
        requireValue(context.candidateId, "candidate"),
      );
    case "CANDIDATE_IP":
      return composite(
        normalizeOpaqueIdentity(requireValue(context.candidateId, "candidate")),
        requireValue(context.trustedIp, "trusted IP"),
      );
    case "ACTOR":
      return normalizeOpaqueIdentity(requireValue(context.actorId, "actor"));
    case "ACTOR_EMAIL_TYPE":
      return composite(
        normalizeOpaqueIdentity(requireValue(context.actorId, "actor")),
        requireValue(context.emailType, "email type").toUpperCase(),
      );
    case "ACTOR_ENTITY":
      return composite(
        normalizeOpaqueIdentity(requireValue(context.actorId, "actor")),
        normalizeOpaqueIdentity(requireValue(context.entityId, "entity")),
      );
  }
}

export function digestRateLimitPrincipal(
  principal: RateLimitPrincipalKind,
  canonicalValue: string,
): string {
  // Deliberately unkeyed SHA-256: this prevents raw identifiers from being
  // stored but is pseudonymization, not anonymization. It avoids inventing a
  // production-only secret solely for the limiter/test environment.
  return createHash("sha256")
    .update(`s08-002:v1:${principal}:${canonicalValue}`, "utf8")
    .digest("hex");
}

export function buildDurableRateLimitRules(
  policyCode: RateLimitPolicyCode,
  context: RateLimitContext,
): DurableRateLimitRule[] {
  const policy = RATE_LIMIT_POLICIES[policyCode];

  if (policy.requiresTrustedIp) {
    requireValue(context.trustedIp, "trusted IP");
  }
  if (policy.requiresEntityAttribution) {
    requireValue(context.entityId, "entity attribution");
  }

  return policy.rules.map((rule) => {
    const principalValue = resolvePrincipal(rule.principal, context);
    return {
      ruleCode: rule.ruleCode,
      keyDigest: digestRateLimitPrincipal(rule.principal, principalValue),
      limit: rule.limit,
      windowSeconds: rule.windowSeconds,
    };
  });
}

function parseInteger(value: unknown): number | null {
  return typeof value === "number" && Number.isInteger(value) && value >= 0
    ? value
    : null;
}

function parseString(value: unknown): string | null {
  return typeof value === "string" && value.length > 0 ? value : null;
}

export async function consumeRateLimit(
  policyCode: RateLimitPolicyCode,
  context: RateLimitContext,
  deps: { client?: RateLimitRpcClient } = {},
): Promise<RateLimitDecision> {
  const rules = buildDurableRateLimitRules(policyCode, context);
  const client =
    deps.client ??
    (createAdminClient() as unknown as RateLimitRpcClient | null);
  if (!client) {
    return {
      allowed: false,
      code: RATE_LIMIT_UNAVAILABLE_CODE,
      policyCode,
    };
  }

  const { data, error } = await client.rpc("consume_rate_limit_rules", {
    p_policy_code: policyCode,
    p_rules: rules,
  });

  if (error || !data || typeof data !== "object") {
    return {
      allowed: false,
      code: RATE_LIMIT_UNAVAILABLE_CODE,
      policyCode,
    };
  }

  const payload = data as Record<string, unknown>;
  if (payload.allowed === true && Array.isArray(payload.rules)) {
    const parsedRules: RateLimitAllowedDecision["rules"] = [];
    for (const item of payload.rules) {
      if (!item || typeof item !== "object") continue;
      const row = item as Record<string, unknown>;
      const ruleCode = parseString(row.ruleCode);
      const limit = parseInteger(row.limit);
      const windowSeconds = parseInteger(row.windowSeconds);
      const remaining = parseInteger(row.remaining);
      const resetAt = parseString(row.resetAt);
      if (
        ruleCode &&
        limit !== null &&
        windowSeconds !== null &&
        remaining !== null &&
        resetAt
      ) {
        parsedRules.push({
          ruleCode,
          limit,
          windowSeconds,
          remaining,
          resetAt,
        });
      }
    }
    return { allowed: true, policyCode, rules: parsedRules };
  }

  if (payload.allowed === false && Array.isArray(payload.blockedRules)) {
    const retryAfterSeconds = parseInteger(payload.retryAfterSeconds);
    if (retryAfterSeconds === null || retryAfterSeconds < 1) {
      return {
        allowed: false,
        code: RATE_LIMIT_UNAVAILABLE_CODE,
        policyCode,
      };
    }

    const blockedRules: RateLimitDeniedDecision["blockedRules"] = [];
    for (const item of payload.blockedRules) {
      if (!item || typeof item !== "object") continue;
      const row = item as Record<string, unknown>;
      const ruleCode = parseString(row.ruleCode);
      const limit = parseInteger(row.limit);
      const windowSeconds = parseInteger(row.windowSeconds);
      const retry = parseInteger(row.retryAfterSeconds);
      const resetAt = parseString(row.resetAt);
      if (
        ruleCode &&
        limit !== null &&
        windowSeconds !== null &&
        retry !== null &&
        retry >= 1 &&
        resetAt
      ) {
        blockedRules.push({
          ruleCode,
          limit,
          windowSeconds,
          retryAfterSeconds: retry,
          resetAt,
        });
      }
    }

    return {
      allowed: false,
      code: RATE_LIMITED_CODE,
      policyCode,
      retryAfterSeconds,
      blockedRules,
    };
  }

  return {
    allowed: false,
    code: RATE_LIMIT_UNAVAILABLE_CODE,
    policyCode,
  };
}
