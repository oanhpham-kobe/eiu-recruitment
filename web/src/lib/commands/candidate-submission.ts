import "server-only";

import type { SupabaseClient } from "@supabase/supabase-js";
import { createCommandRunner } from "@/lib/commands/runner";
import {
  CommandErrorCode,
  type CommandResult,
  type TrustedCommandDefinition,
  type VerifiedActor,
} from "@/lib/commands/types";
import { createServerClient } from "@/lib/supabase/server";

const UUID_REGEX =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

// -----------------------------------------------------------------------------
// Type Definitions
// -----------------------------------------------------------------------------

export type EducationItem = {
  institutionName: string;
  degreeName: string;
  major?: string | null;
  startYear: number;
  endYear?: number | null;
  gpa?: string | null;
  sortOrder?: number;
};

export type WorkExperienceItem = {
  companyName: string;
  positionTitle: string;
  startDate?: string | null;
  endDate?: string | null;
  isCurrent?: boolean;
  description?: string | null;
  sortOrder?: number;
};

export type ActivityItem = {
  activityName: string;
  roleTitle?: string | null;
  organizationName?: string | null;
  startDate?: string | null;
  endDate?: string | null;
  description?: string | null;
  sortOrder?: number;
};

export type SubmitCandidateSubmissionInput = {
  candidateFormSessionId: string;
  fullName: string;
  phone?: string | null;
  dateOfBirth?: string | null;
  gender?: "MALE" | "FEMALE" | "OTHER" | string | null;
  address?: string | null;
  candidateNotes?: string | null;
  education?: EducationItem[];
  workExperiences?: WorkExperienceItem[];
  activities?: ActivityItem[];
  privacyNoticeVersion: string;
  idempotencyKey?: string;
};

export type SubmitCandidateSubmissionData = {
  submission_id: string;
  status_code: "NEW";
  version_no: number;
  submitted_at: string;
};

export type UpdateCandidateSubmissionInput = SubmitCandidateSubmissionInput;

export type UpdateCandidateSubmissionData = {
  submission_id: string;
  status_code: "NEW";
  version_no: number;
  updated_at: string;
};

export type CandidateSubmissionCommandDeps = {
  client?: SupabaseClient;
  resolveActor?: () => Promise<VerifiedActor | null>;
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
    error,
  } = await supabase.auth.getUser();

  if (error || !user || !user.email) {
    return null;
  }

  const { data: candidate } = await supabase
    .from("candidates")
    .select("candidate_id, is_active")
    .eq("auth_user_id", user.id)
    .maybeSingle();

  if (!candidate || typeof candidate !== "object") {
    return null;
  }

  const isActive = Boolean(
    "is_active" in candidate && candidate.is_active === true,
  );

  return {
    authUserId: user.id,
    email: user.email,
    isActive,
    roles: ["CANDIDATE"],
    permissions: ["candidate.self"],
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
  if (!name || name.length > 120) {
    return {
      valid: false,
      error: "Full name is required and must not exceed 120 characters",
    };
  }

  if (input.phone && input.phone.trim().length > 30) {
    return {
      valid: false,
      error: "Phone number must not exceed 30 characters",
    };
  }

  if (
    input.gender &&
    !["MALE", "FEMALE", "OTHER"].includes(input.gender.toUpperCase())
  ) {
    return { valid: false, error: "Gender must be MALE, FEMALE, or OTHER" };
  }

  if (input.address && input.address.trim().length > 255) {
    return { valid: false, error: "Address must not exceed 255 characters" };
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
    institution_name: e.institutionName.trim(),
    degree_name: e.degreeName.trim(),
    major: e.major?.trim() || null,
    start_year: e.startYear,
    end_year: e.endYear ?? null,
    gpa: e.gpa?.trim() || null,
    sort_order: e.sortOrder ?? idx,
  }));

  const workExperiences = (input.workExperiences ?? []).map((w, idx) => ({
    company_name: w.companyName.trim(),
    position_title: w.positionTitle.trim(),
    start_date: w.startDate ?? null,
    end_date: w.endDate ?? null,
    is_current: Boolean(w.isCurrent),
    description: w.description?.trim() || null,
    sort_order: w.sortOrder ?? idx,
  }));

  const activities = (input.activities ?? []).map((a, idx) => ({
    activity_name: a.activityName.trim(),
    role_title: a.roleTitle?.trim() || null,
    organization_name: a.organizationName?.trim() || null,
    start_date: a.startDate ?? null,
    end_date: a.endDate ?? null,
    description: a.description?.trim() || null,
    sort_order: a.sortOrder ?? idx,
  }));

  return { education, workExperiences, activities };
}

// -----------------------------------------------------------------------------
// 1. Submit Candidate Submission Command
// -----------------------------------------------------------------------------

export function createSubmitCandidateSubmissionCommand(
  supabase: SupabaseClient,
): TrustedCommandDefinition<
  SubmitCandidateSubmissionInput,
  string | undefined,
  SubmitCandidateSubmissionInput,
  SubmitCandidateSubmissionData
> {
  return {
    name: "submit_candidate_submission",
    extractTarget(input) {
      return input.candidateFormSessionId;
    },
    authorize(actor) {
      const isCandidate =
        actor.roles.includes("CANDIDATE") ||
        actor.permissions.includes("candidate.self");

      if (!isCandidate) {
        return {
          authorized: false,
          code: CommandErrorCode.FORBIDDEN,
          reason: "Candidate authorization required",
        };
      }

      return { authorized: true };
    },
    validate(input) {
      const result = validateSubmissionPayload(input);
      if (!result.valid) {
        return { success: false, error: result.error ?? "Validation failed" };
      }
      return { success: true, data: input };
    },
    async execute(_actor, validated) {
      const { education, workExperiences, activities } =
        formatChildArrays(validated);

      const { data, error } = await supabase.rpc(
        "submit_candidate_submission",
        {
          p_candidate_form_session_id: validated.candidateFormSessionId,
          p_full_name: validated.fullName.trim(),
          p_phone: validated.phone?.trim() || null,
          p_date_of_birth: validated.dateOfBirth || null,
          p_gender: validated.gender ? validated.gender.toUpperCase() : null,
          p_address: validated.address?.trim() || null,
          p_candidate_notes: validated.candidateNotes?.trim() || null,
          p_education: education,
          p_work_experiences: workExperiences,
          p_activities: activities,
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
      };

      if (!result.success || !result.data) {
        const rawCode = result.error_code ? String(result.error_code) : "";
        const code =
          CommandErrorCode[rawCode as keyof typeof CommandErrorCode] ??
          CommandErrorCode.INTERNAL_ERROR;
        return {
          success: false,
          error: {
            code,
            message: result.message || "Failed to submit candidate submission",
          },
        };
      }

      return {
        success: true,
        data: result.data,
      };
    },
  };
}

// -----------------------------------------------------------------------------
// 2. Update Candidate Submission Command
// -----------------------------------------------------------------------------

export function createUpdateCandidateSubmissionCommand(
  supabase: SupabaseClient,
): TrustedCommandDefinition<
  UpdateCandidateSubmissionInput,
  string | undefined,
  UpdateCandidateSubmissionInput,
  UpdateCandidateSubmissionData
> {
  return {
    name: "update_candidate_submission",
    extractTarget(input) {
      return input.candidateFormSessionId;
    },
    authorize(actor) {
      const isCandidate =
        actor.roles.includes("CANDIDATE") ||
        actor.permissions.includes("candidate.self");

      if (!isCandidate) {
        return {
          authorized: false,
          code: CommandErrorCode.FORBIDDEN,
          reason: "Candidate authorization required",
        };
      }

      return { authorized: true };
    },
    validate(input) {
      const result = validateSubmissionPayload(input);
      if (!result.valid) {
        return { success: false, error: result.error ?? "Validation failed" };
      }
      return { success: true, data: input };
    },
    async execute(_actor, validated) {
      const { education, workExperiences, activities } =
        formatChildArrays(validated);

      const { data, error } = await supabase.rpc(
        "update_candidate_submission",
        {
          p_candidate_form_session_id: validated.candidateFormSessionId,
          p_full_name: validated.fullName.trim(),
          p_phone: validated.phone?.trim() || null,
          p_date_of_birth: validated.dateOfBirth || null,
          p_gender: validated.gender ? validated.gender.toUpperCase() : null,
          p_address: validated.address?.trim() || null,
          p_candidate_notes: validated.candidateNotes?.trim() || null,
          p_education: education,
          p_work_experiences: workExperiences,
          p_activities: activities,
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
      };

      if (!result.success || !result.data) {
        const rawCode = result.error_code ? String(result.error_code) : "";
        const code =
          CommandErrorCode[rawCode as keyof typeof CommandErrorCode] ??
          CommandErrorCode.INTERNAL_ERROR;
        return {
          success: false,
          error: {
            code,
            message: result.message || "Failed to update candidate submission",
          },
        };
      }

      return {
        success: true,
        data: result.data,
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
  const supabase = deps.client ?? (await createServerClient());
  const resolveActor =
    deps.resolveActor ?? (() => defaultResolveActor(supabase));
  const runner = createCommandRunner({ resolveActor });
  return runner(createSubmitCandidateSubmissionCommand(supabase), input);
}

export async function updateCandidateSubmission(
  input: UpdateCandidateSubmissionInput,
  deps: CandidateSubmissionCommandDeps = {},
): Promise<CommandResult<UpdateCandidateSubmissionData>> {
  const supabase = deps.client ?? (await createServerClient());
  const resolveActor =
    deps.resolveActor ?? (() => defaultResolveActor(supabase));
  const runner = createCommandRunner({ resolveActor });
  return runner(createUpdateCandidateSubmissionCommand(supabase), input);
}
