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

export type OpenSubmissionInput = {
  submissionId: string;
};

export type OpenSubmissionData = {
  submission_id: string;
  candidate_id: string;
  status_code: string;
  full_name: string;
  email: string;
  phone: string | null;
  date_of_birth: string | null;
  gender: string | null;
  address: string | null;
  candidate_notes: string | null;
  submitted_at: string;
  version_no: number;
};

export type SetSubmissionManualStatusInput = {
  candidateId: string;
  statusCode: "NEW" | "READ";
  expectedLatestSubmissionId: string;
  expectedVersion: number;
  idempotencyKey?: string;
};

export type SetSubmissionManualStatusData = {
  submission_id: string;
  status_code: "NEW" | "READ";
  version_no: number;
};

export type RecalculateSubmissionStatusInput = {
  submissionId: string;
};

export type RecalculateSubmissionStatusData = {
  submission_id: string;
  status_code: string;
  previous_status_code: string;
};

export type SubmissionStatusCommandDeps = {
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

  // Check internal user role
  const { data: appUser } = await supabase
    .from("app_users")
    .select("app_user_id, is_active, is_root")
    .eq("auth_user_id", user.id)
    .maybeSingle();

  if (appUser && typeof appUser === "object" && appUser.is_active) {
    return {
      authUserId: user.id,
      email: user.email,
      isActive: true,
      roles: appUser.is_root ? ["ROOT_ADMIN", "HR"] : ["HR"],
      permissions: ["submissions.view", "submissions.status"],
    };
  }

  return {
    authUserId: user.id,
    email: user.email,
    isActive: true,
    roles: ["GUEST"],
    permissions: [],
  };
}

// -----------------------------------------------------------------------------
// 1. Open Submission Command
// -----------------------------------------------------------------------------

export function createOpenSubmissionCommand(
  supabase: SupabaseClient,
): TrustedCommandDefinition<
  OpenSubmissionInput,
  string | undefined,
  OpenSubmissionInput,
  OpenSubmissionData
> {
  return {
    name: "open_submission",
    extractTarget(input) {
      return input.submissionId;
    },
    authorize(actor) {
      const canView =
        actor.permissions.includes("submissions.view") ||
        actor.roles.includes("ROOT_ADMIN") ||
        actor.roles.includes("HR");

      if (!canView) {
        return {
          authorized: false,
          code: CommandErrorCode.FORBIDDEN,
          reason: "Permission submissions.view required",
        };
      }

      return { authorized: true };
    },
    validate(input) {
      if (!input.submissionId || !UUID_REGEX.test(input.submissionId)) {
        return {
          success: false,
          error: "Invalid submissionId UUID",
        };
      }
      return { success: true, data: input };
    },
    async execute(_actor, validated) {
      const { data, error } = await supabase.rpc("open_submission", {
        p_submission_id: validated.submissionId,
      });

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
        data?: OpenSubmissionData;
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
            message: result.message || "Failed to open submission",
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
// 2. Set Submission Manual Status Command (NEW <-> READ)
// -----------------------------------------------------------------------------

export function createSetSubmissionManualStatusCommand(
  supabase: SupabaseClient,
): TrustedCommandDefinition<
  SetSubmissionManualStatusInput,
  string | undefined,
  SetSubmissionManualStatusInput,
  SetSubmissionManualStatusData
> {
  return {
    name: "set_submission_manual_status",
    extractTarget(input) {
      return input.expectedLatestSubmissionId;
    },
    authorize(actor) {
      const canChangeStatus =
        actor.permissions.includes("submissions.status") ||
        actor.roles.includes("ROOT_ADMIN") ||
        actor.roles.includes("HR");

      if (!canChangeStatus) {
        return {
          authorized: false,
          code: CommandErrorCode.FORBIDDEN,
          reason: "Permission submissions.status required",
        };
      }

      return { authorized: true };
    },
    validate(input) {
      if (!input.candidateId || !UUID_REGEX.test(input.candidateId)) {
        return {
          success: false,
          error: "Invalid candidateId UUID",
        };
      }

      if (
        !input.expectedLatestSubmissionId ||
        !UUID_REGEX.test(input.expectedLatestSubmissionId)
      ) {
        return {
          success: false,
          error: "Invalid expectedLatestSubmissionId UUID",
        };
      }

      if (!["NEW", "READ"].includes(input.statusCode)) {
        return {
          success: false,
          error:
            "Manual status change permits only NEW or READ. PROCESSED, DONE, and CLOSED are system-derived.",
        };
      }

      if (
        typeof input.expectedVersion !== "number" ||
        input.expectedVersion < 1
      ) {
        return {
          success: false,
          error: "expectedVersion must be a positive integer",
        };
      }

      if (input.idempotencyKey && !UUID_REGEX.test(input.idempotencyKey)) {
        return {
          success: false,
          error: "idempotencyKey must be a valid UUID",
        };
      }

      return { success: true, data: input };
    },
    async execute(_actor, validated) {
      const { data, error } = await supabase.rpc(
        "set_submission_manual_status",
        {
          p_candidate_id: validated.candidateId,
          p_status_code: validated.statusCode,
          p_expected_latest_submission_id: validated.expectedLatestSubmissionId,
          p_expected_version: validated.expectedVersion,
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
        data?: SetSubmissionManualStatusData;
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
            message:
              result.message || "Failed to update submission manual status",
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
// 3. Recalculate Submission Status Command
// -----------------------------------------------------------------------------

export function createRecalculateSubmissionStatusCommand(
  supabase: SupabaseClient,
): TrustedCommandDefinition<
  RecalculateSubmissionStatusInput,
  string | undefined,
  RecalculateSubmissionStatusInput,
  RecalculateSubmissionStatusData
> {
  return {
    name: "recalculate_submission_status",
    extractTarget(input) {
      return input.submissionId;
    },
    authorize(actor) {
      const isInternal =
        actor.roles.includes("HR") ||
        actor.roles.includes("ROOT_ADMIN") ||
        actor.roles.includes("SERVICE_ROLE");

      if (!isInternal) {
        return {
          authorized: false,
          code: CommandErrorCode.FORBIDDEN,
          reason: "Internal staff authorization required",
        };
      }

      return { authorized: true };
    },
    validate(input) {
      if (!input.submissionId || !UUID_REGEX.test(input.submissionId)) {
        return {
          success: false,
          error: "Invalid submissionId UUID",
        };
      }
      return { success: true, data: input };
    },
    async execute(_actor, validated) {
      const { data, error } = await supabase.rpc(
        "recalculate_submission_status",
        {
          p_submission_id: validated.submissionId,
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
        data?: RecalculateSubmissionStatusData;
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
            message:
              result.message || "Failed to recalculate submission status",
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
// Public Helpers
// -----------------------------------------------------------------------------

export async function openSubmission(
  input: OpenSubmissionInput,
  deps: SubmissionStatusCommandDeps = {},
): Promise<CommandResult<OpenSubmissionData>> {
  const supabase = deps.client ?? (await createServerClient());
  const resolveActor =
    deps.resolveActor ?? (() => defaultResolveActor(supabase));
  const runner = createCommandRunner({ resolveActor });
  return runner(createOpenSubmissionCommand(supabase), input);
}

export async function setSubmissionManualStatus(
  input: SetSubmissionManualStatusInput,
  deps: SubmissionStatusCommandDeps = {},
): Promise<CommandResult<SetSubmissionManualStatusData>> {
  const supabase = deps.client ?? (await createServerClient());
  const resolveActor =
    deps.resolveActor ?? (() => defaultResolveActor(supabase));
  const runner = createCommandRunner({ resolveActor });
  return runner(createSetSubmissionManualStatusCommand(supabase), input);
}

export async function recalculateSubmissionStatus(
  input: RecalculateSubmissionStatusInput,
  deps: SubmissionStatusCommandDeps = {},
): Promise<CommandResult<RecalculateSubmissionStatusData>> {
  const supabase = deps.client ?? (await createServerClient());
  const resolveActor =
    deps.resolveActor ?? (() => defaultResolveActor(supabase));
  const runner = createCommandRunner({ resolveActor });
  return runner(createRecalculateSubmissionStatusCommand(supabase), input);
}
