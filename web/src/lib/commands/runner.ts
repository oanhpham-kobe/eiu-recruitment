import "server-only";

import { logError } from "@/lib/logging/logger";

import {
  CommandErrorCode,
  type CommandResult,
  type TrustedCommandDefinition,
  type VerifiedActor,
} from "./types";

export function createCommandRunner(deps: {
  resolveActor: () => Promise<VerifiedActor | null>;
}) {
  return async function executeCommand<
    TRawInput,
    TTarget,
    TValidatedInput,
    TOutput,
  >(
    command: TrustedCommandDefinition<
      TRawInput,
      TTarget,
      TValidatedInput,
      TOutput
    >,
    rawInput: TRawInput,
  ): Promise<CommandResult<TOutput>> {
    try {
      const actor = await deps.resolveActor();

      if (!actor) {
        return {
          success: false,
          error: {
            code: CommandErrorCode.UNAUTHENTICATED,
            message: "Authentication required",
          },
        };
      }

      if (!actor.isActive) {
        return {
          success: false,
          error: {
            code: CommandErrorCode.USER_INACTIVE,
            message: "User account is inactive",
          },
        };
      }

      const target = command.extractTarget?.(rawInput);
      const authorization = await command.authorize(actor, target);

      if (!authorization.authorized) {
        return {
          success: false,
          error: {
            code: authorization.code ?? CommandErrorCode.FORBIDDEN,
            message: authorization.reason ?? "Insufficient permissions",
          },
        };
      }

      const validation = command.validate(rawInput);

      if (!validation.success) {
        return {
          success: false,
          error: {
            code: CommandErrorCode.VALIDATION_ERROR,
            message: validation.error,
            details: validation.details,
          },
        };
      }

      return {
        success: true,
        data: await command.execute(actor, validation.data),
      };
    } catch (error) {
      logError(error);

      return {
        success: false,
        error: {
          code: CommandErrorCode.INTERNAL_ERROR,
          message: "Internal command error",
        },
      };
    }
  };
}
