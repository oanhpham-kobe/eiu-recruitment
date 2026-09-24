import "server-only";

export const RATE_LIMIT_POLICY_CODES = [
  "CANDIDATE_OTP_REQUEST",
  "CANDIDATE_OTP_VERIFY",
  "CANDIDATE_SUBMIT",
  "CANDIDATE_UPDATE",
  "UPLOAD",
  "INTERNAL_SEARCH",
  "EMAIL_ENQUEUE",
  "PDF_GENERATION",
] as const;

export type RateLimitPolicyCode = (typeof RATE_LIMIT_POLICY_CODES)[number];

export type RateLimitPrincipalKind =
  | "EMAIL"
  | "IDENTITY"
  | "TRUSTED_IP"
  | "CANDIDATE"
  | "CANDIDATE_IP"
  | "ACTOR"
  | "ACTOR_EMAIL_TYPE"
  | "ACTOR_ENTITY";

export type RateLimitRuleDefinition = Readonly<{
  ruleCode: string;
  principal: RateLimitPrincipalKind;
  limit: number;
  windowSeconds: number;
}>;

export type RateLimitPolicyDefinition = Readonly<{
  code: RateLimitPolicyCode;
  rules: readonly RateLimitRuleDefinition[];
  requiresTrustedIp?: boolean;
  requiresEntityAttribution?: boolean;
}>;

export const RATE_LIMIT_POLICIES: Readonly<
  Record<RateLimitPolicyCode, RateLimitPolicyDefinition>
> = {
  CANDIDATE_OTP_REQUEST: {
    code: "CANDIDATE_OTP_REQUEST",
    rules: [
      {
        ruleCode: "EMAIL_15M",
        principal: "EMAIL",
        limit: 5,
        windowSeconds: 15 * 60,
      },
      {
        ruleCode: "IP_15M",
        principal: "TRUSTED_IP",
        limit: 20,
        windowSeconds: 15 * 60,
      },
    ],
  },
  CANDIDATE_OTP_VERIFY: {
    code: "CANDIDATE_OTP_VERIFY",
    rules: [
      {
        ruleCode: "IDENTITY_15M",
        principal: "IDENTITY",
        limit: 10,
        windowSeconds: 15 * 60,
      },
      {
        ruleCode: "IP_15M",
        principal: "TRUSTED_IP",
        limit: 50,
        windowSeconds: 15 * 60,
      },
    ],
  },
  CANDIDATE_SUBMIT: {
    code: "CANDIDATE_SUBMIT",
    requiresTrustedIp: true,
    rules: [
      {
        ruleCode: "CANDIDATE_1H",
        principal: "CANDIDATE",
        limit: 5,
        windowSeconds: 60 * 60,
      },
      {
        ruleCode: "CANDIDATE_1D",
        principal: "CANDIDATE",
        limit: 20,
        windowSeconds: 24 * 60 * 60,
      },
    ],
  },
  CANDIDATE_UPDATE: {
    code: "CANDIDATE_UPDATE",
    rules: [
      {
        ruleCode: "CANDIDATE_IP_15M",
        principal: "CANDIDATE_IP",
        limit: 30,
        windowSeconds: 15 * 60,
      },
    ],
  },
  UPLOAD: {
    code: "UPLOAD",
    rules: [
      {
        ruleCode: "IDENTITY_15M",
        principal: "IDENTITY",
        limit: 30,
        windowSeconds: 15 * 60,
      },
      {
        ruleCode: "IP_15M",
        principal: "TRUSTED_IP",
        limit: 100,
        windowSeconds: 15 * 60,
      },
    ],
  },
  INTERNAL_SEARCH: {
    code: "INTERNAL_SEARCH",
    rules: [
      {
        ruleCode: "ACTOR_1M",
        principal: "ACTOR",
        limit: 120,
        windowSeconds: 60,
      },
    ],
  },
  EMAIL_ENQUEUE: {
    code: "EMAIL_ENQUEUE",
    requiresEntityAttribution: true,
    rules: [
      {
        ruleCode: "ACTOR_TYPE_1H",
        principal: "ACTOR_EMAIL_TYPE",
        limit: 60,
        windowSeconds: 60 * 60,
      },
      {
        ruleCode: "ACTOR_TYPE_1M",
        principal: "ACTOR_EMAIL_TYPE",
        limit: 10,
        windowSeconds: 60,
      },
    ],
  },
  PDF_GENERATION: {
    code: "PDF_GENERATION",
    rules: [
      {
        ruleCode: "ACTOR_ENTITY_1H",
        principal: "ACTOR_ENTITY",
        limit: 20,
        windowSeconds: 60 * 60,
      },
    ],
  },
};
