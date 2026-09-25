import "server-only";

import type { SupabaseClient } from "@supabase/supabase-js";
import { createCommandRunner } from "@/lib/commands/runner";
import {
  CommandErrorCode,
  type CommandResult,
  type TrustedCommandDefinition,
  type VerifiedActor,
} from "@/lib/commands/types";
import {
  buildDurableRateLimitRules,
  digestRateLimitPrincipal,
} from "@/lib/security/rate-limit";
import { createServerClient } from "@/lib/supabase/server";

const UUID_REGEX =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

// -----------------------------------------------------------------------------
// Type Definitions
// -----------------------------------------------------------------------------

export type EducationItem = {
  periodText?: string | null;
  qualificationId?: string | null;
  major?: string | null;
  institution?: string | null;
  sortOrder?: number;
};

export type SubmitCandidateSubmissionInput = {
  candidateFormSessionId: string;
  fullName: string;
  phone: string;
  dateOfBirth: string;
  gender: "MALE" | "FEMALE" | string;
  address: string;
  education?: EducationItem[];
  privacyNoticeVersion: string;
  idempotencyKey?: string;
};

export type SubmitCandidateSubmissionData = {
  submission_id: string;
  status_code: "NEW";
  version_no: number;
  submitted_at?: string;
};

export type UpdateCandidateSubmissionInput = SubmitCandidateSubmissionInput;

export type UpdateCandidateSubmissionData = {
  submission_id: string;
  status_code: "NEW";
  version_no: number;
  updated_at?: string;
};

export type CandidateSubmissionCommandDeps = {
  supabase?: SupabaseClient;
  client?: SupabaseClient;
  actorClient?: SupabaseClient;
  trustedIp?: string;
  resolveActor?: (client?: SupabaseClient) => Promise<VerifiedActor | null>;
};

// -----------------------------------------------------------------------------
// Default Actor Resolution
// -----------------------------------------------------------------------------

async function defaultResolveActor(
  client?: SupabaseClient,
): Promise<VerifiedActor | null> {
  const supabase = client ?? (await createServerClient());
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user?.email) {
    return null;
  }

  const { data: candidate } = await supabase
    .from("candidates")
    .select("candidate_id, is_active")
    .eq("auth_user_id", user.id)
    .maybeSingle();

  if (!candidate) {
    return null;
  }

  return {
    authUserId: user.id,
    candidateId: candidate.candidate_id,
    email: user.email,
    isActive: candidate.is_active,
    roles: ["candidate"],
    permissions: ["candidate_self"],
  };
}

// -----------------------------------------------------------------------------
// Validation Helper
// -----------------------------------------------------------------------------

function validateSubmissionPayload(input: SubmitCandidateSubmissionInput): {
  valid: boolean;
  error?: string;
} {
  if (
    !input.candidateFormSessionId ||
    !UUID_REGEX.test(input.candidateFormSessionId)
  ) {
    return { valid: false, error: "Invalid candidateFormSessionId UUID" };
  }

  const name = input.fullName?.trim();
  if (!name || name.length > 200) {
    return {
      valid: false,
      error: "Full name is required and must not exceed 200 characters",
    };
  }

  const phone = input.phone?.trim();
  if (!phone || phone.length > 32) {
    return {
      valid: false,
      error: "Phone number is required and must not exceed 32 characters",
    };
  }

  if (!input.dateOfBirth?.trim()) {
    return { valid: false, error: "Date of birth is required" };
  }

  const dob = input.dateOfBirth.trim();
  if (dob < "1900-01-01") {
    return {
      valid: false,
      error: "Date of birth must be on or after 1900-01-01",
    };
  }

  const today = new Date().toISOString().split("T")[0];
  if (dob > today) {
    return { valid: false, error: "Date of birth cannot be in the future" };
  }

  const gender = input.gender?.toUpperCase()?.trim();
  if (!gender || !["MALE", "FEMALE"].includes(gender)) {
    return { valid: false, error: "Gender must be MALE or FEMALE" };
  }

  const address = input.address?.trim();
  if (!address || address.length > 500) {
    return {
      valid: false,
      error: "Address is required and must not exceed 500 characters",
    };
  }

  if (input.education) {
    if (!Array.isArray(input.education)) {
      return { valid: false, error: "Education must be an array" };
    }
    if (input.education.length > 20) {
      return { valid: false, error: "Education cannot exceed 20 rows" };
    }
    for (const edu of input.education) {
      if (edu.qualificationId && !UUID_REGEX.test(edu.qualificationId)) {
        return { valid: false, error: "Invalid qualificationId UUID" };
      }
      if (edu.periodText && edu.periodText.trim().length > 100) {
        return {
          valid: false,
          error: "Education period text must not exceed 100 characters",
        };
      }
      if (edu.major && edu.major.trim().length > 255) {
        return {
          valid: false,
          error: "Education major must not exceed 255 characters",
        };
      }
      if (edu.institution && edu.institution.trim().length > 255) {
        return {
          valid: false,
          error: "Education institution must not exceed 255 characters",
        };
      }
    }
  }

  if (!input.privacyNoticeVersion?.trim()) {
    return {
      valid: false,
      error: "Acknowledged privacy notice version is required",
    };
  }

  if (input.idempotencyKey && !UUID_REGEX.test(input.idempotencyKey)) {
    return { valid: false, error: "Idempotency key must be a valid UUID" };
  }

  return { valid: true };
}

function formatChildArrays(input: SubmitCandidateSubmissionInput) {
  const education = (input.education ?? []).map((e, idx) => ({
    period_text: e.periodText?.trim() || null,
    qualification_id: e.qualificationId?.trim() || null,
    major: e.major?.trim() || null,
    institution: e.institution?.trim() || null,
    sort_order: e.sortOrder ?? idx + 1,
  }));

  return { education };
}

// -----------------------------------------------------------------------------
// 1. Submit Candidate Submission Command
// -----------------------------------------------------------------------------

export function createSubmitCandidateSubmissionCommand(
  supabase: SupabaseClient,
  trustedIp?: string,
): TrustedCommandDefinition<
  SubmitCandidateSubmissionInput,
  string,
  SubmitCandidateSubmissionInput,
  SubmitCandidateSubmissionData
> {
  return {
    name: "submit_candidate_submission",

    extractTarget(rawInput) {
      return rawInput.candidateFormSessionId;
    },

    authorize(actor) {
      const isCandidate =
        actor.roles.some((r) => r.toLowerCase() === "candidate") ||
        actor.permissions.includes("candidate.self") ||
        actor.permissions.includes("candidate_self");
      if (!isCandidate) {
        return {
          authorized: false,
          code: CommandErrorCode.FORBIDDEN,
          reason: "Candidate authorization required",
        };
      }
      return { authorized: true };
    },

    validate(rawInput) {
      const result = validateSubmissionPayload(rawInput);
      if (!result.valid) {
        return { success: false, error: result.error ?? "Validation error" };
      }
      return { success: true, data: rawInput };
    },

    async execute(actor, validated) {
      const { education } = formatChildArrays(validated);
      if (!actor.candidateId || !trustedIp) {
        return {
          success: false,
          error: {
            code: CommandErrorCode.RATE_LIMIT_UNAVAILABLE,
            message: "Request protection context is unavailable",
          },
        };
      }
      const rules = buildDurableRateLimitRules("CANDIDATE_SUBMIT", {
        candidateId: actor.candidateId,
        trustedIp,
      });
      const candidateKeyDigest = rules.find(
        (rule) => rule.ruleCode === "CANDIDATE_1H",
      )?.keyDigest;
      if (!candidateKeyDigest) {
        return {
          success: false,
          error: {
            code: CommandErrorCode.RATE_LIMIT_UNAVAILABLE,
            message: "Request protection context is unavailable",
          },
        };
      }

      const { data, error } = await supabase.rpc(
        "submit_candidate_submission_rate_limited",
        {
          p_actor_auth_user_id: actor.authUserId,
          p_candidate_key_digest: candidateKeyDigest,
          p_trusted_ip_key_digest: digestRateLimitPrincipal(
            "TRUSTED_IP",
            trustedIp,
          ),
          p_candidate_form_session_id: validated.candidateFormSessionId,
          p_full_name: validated.fullName.trim(),
          p_phone: validated.phone.trim(),
          p_date_of_birth: validated.dateOfBirth.trim(),
          p_gender: validated.gender.toUpperCase().trim(),
          p_address: validated.address.trim(),
          p_education: education,
          p_privacy_notice_version: validated.privacyNoticeVersion.trim(),
          p_idempotency_key: validated.idempotencyKey ?? crypto.randomUUID(),
        },
      );

      if (error) {
        return {
          success: false,
          error: {
            code: CommandErrorCode.INTERNAL_ERROR,
            message: error.message,
          },
        };
      }

      const result = data as {
        success: boolean;
        error_code?: string;
        message?: string;
        data?: SubmitCandidateSubmissionData;
        submission_id?: string;
        status_code?: "NEW";
        version_no?: number;
      };

      if (!result.success) {
        const rawCode = result.error_code ? String(result.error_code) : "";
        const code =
          CommandErrorCode[rawCode as keyof typeof CommandErrorCode] ??
          CommandErrorCode.INTERNAL_ERROR;
        return {
          success: false,
          error: {
            code,
            message: result.message || "Failed to submit candidate submission",
            details: result.data,
          },
        };
      }

      const returnData: SubmitCandidateSubmissionData = result.data ?? {
        submission_id: result.submission_id ?? "",
        status_code: result.status_code ?? "NEW",
        version_no: result.version_no ?? 1,
      };

      return {
        success: true,
        data: returnData,
      };
    },
  };
}

// -----------------------------------------------------------------------------
// 2. Update Candidate Submission Command
// -----------------------------------------------------------------------------

export function createUpdateCandidateSubmissionCommand(
  supabase: SupabaseClient,
  trustedIp?: string,
): TrustedCommandDefinition<
  UpdateCandidateSubmissionInput,
  string,
  UpdateCandidateSubmissionInput,
  UpdateCandidateSubmissionData
> {
  return {
    name: "update_candidate_submission",

    extractTarget(rawInput) {
      return rawInput.candidateFormSessionId;
    },

    authorize(actor) {
      const isCandidate =
        actor.roles.some((r) => r.toLowerCase() === "candidate") ||
        actor.permissions.includes("candidate.self") ||
        actor.permissions.includes("candidate_self");
      if (!isCandidate) {
        return {
          authorized: false,
          code: CommandErrorCode.FORBIDDEN,
          reason: "Candidate authorization required",
        };
      }
      return { authorized: true };
    },

    validate(rawInput) {
      const result = validateSubmissionPayload(rawInput);
      if (!result.valid) {
        return { success: false, error: result.error ?? "Validation error" };
      }
      return { success: true, data: rawInput };
    },

    async execute(actor, validated) {
      const { education } = formatChildArrays(validated);
      if (!actor.candidateId || !trustedIp) {
        return {
          success: false,
          error: {
            code: CommandErrorCode.RATE_LIMIT_UNAVAILABLE,
            message: "Request protection context is unavailable",
          },
        };
      }
      const candidateIpKeyDigest = buildDurableRateLimitRules(
        "CANDIDATE_UPDATE",
        { candidateId: actor.candidateId, trustedIp },
      )[0]?.keyDigest;
      if (!candidateIpKeyDigest) {
        return {
          success: false,
          error: {
            code: CommandErrorCode.RATE_LIMIT_UNAVAILABLE,
            message: "Request protection context is unavailable",
          },
        };
      }

      const { data, error } = await supabase.rpc(
        "update_candidate_submission_rate_limited",
        {
          p_actor_auth_user_id: actor.authUserId,
          p_candidate_ip_key_digest: candidateIpKeyDigest,
          p_candidate_form_session_id: validated.candidateFormSessionId,
          p_full_name: validated.fullName.trim(),
          p_phone: validated.phone.trim(),
          p_date_of_birth: validated.dateOfBirth.trim(),
          p_gender: validated.gender.toUpperCase().trim(),
          p_address: validated.address.trim(),
          p_education: education,
          p_privacy_notice_version: validated.privacyNoticeVersion.trim(),
          p_idempotency_key: validated.idempotencyKey ?? crypto.randomUUID(),
        },
      );

      if (error) {
        return {
          success: false,
          error: {
            code: CommandErrorCode.INTERNAL_ERROR,
            message: error.message,
          },
        };
      }

      const result = data as {
        success: boolean;
        error_code?: string;
        message?: string;
        data?: UpdateCandidateSubmissionData;
        submission_id?: string;
        status_code?: "NEW";
        version_no?: number;
      };

      if (!result.success) {
        const rawCode = result.error_code ? String(result.error_code) : "";
        const code =
          CommandErrorCode[rawCode as keyof typeof CommandErrorCode] ??
          CommandErrorCode.INTERNAL_ERROR;
        return {
          success: false,
          error: {
            code,
            message: result.message || "Failed to update candidate submission",
            details: result.data,
          },
        };
      }

      const returnData: UpdateCandidateSubmissionData = result.data ?? {
        submission_id: result.submission_id ?? "",
        status_code: result.status_code ?? "NEW",
        version_no: result.version_no ?? 1,
      };

      return {
        success: true,
        data: returnData,
      };
    },
  };
}

// -----------------------------------------------------------------------------
// Public Helper Functions
// -----------------------------------------------------------------------------

export async function submitCandidateSubmission(
  input: SubmitCandidateSubmissionInput,
  deps: CandidateSubmissionCommandDeps = {},
): Promise<CommandResult<SubmitCandidateSubmissionData>> {
  const actorClient =
    deps.actorClient ?? deps.client ?? (await createServerClient());
  const mutationClient = deps.supabase ?? deps.client ?? actorClient;
  const resolveActor =
    deps.resolveActor ?? (() => defaultResolveActor(actorClient));
  const runner = createCommandRunner({ resolveActor });
  return runner(
    createSubmitCandidateSubmissionCommand(mutationClient, deps.trustedIp),
    input,
  );
}

export async function updateCandidateSubmission(
  input: UpdateCandidateSubmissionInput,
  deps: CandidateSubmissionCommandDeps = {},
): Promise<CommandResult<UpdateCandidateSubmissionData>> {
  const actorClient =
    deps.actorClient ?? deps.client ?? (await createServerClient());
  const mutationClient = deps.supabase ?? deps.client ?? actorClient;
  const resolveActor =
    deps.resolveActor ?? (() => defaultResolveActor(actorClient));
  const runner = createCommandRunner({ resolveActor });
  return runner(
    createUpdateCandidateSubmissionCommand(mutationClient, deps.trustedIp),
    input,
  );
}
