export enum CommandErrorCode {
  UNAUTHENTICATED = "UNAUTHENTICATED",
  FORBIDDEN = "FORBIDDEN",
  NOT_FOUND = "NOT_FOUND",
  INVALID_STATE = "INVALID_STATE",
  VALIDATION_ERROR = "VALIDATION_ERROR",
  STALE_VERSION = "STALE_VERSION",
  FORM_SESSION_EXPIRED = "FORM_SESSION_EXPIRED",
  UPLOAD_RESERVATION_EXPIRED = "UPLOAD_RESERVATION_EXPIRED",
  DUPLICATE_APPLICATION = "DUPLICATE_APPLICATION",
  APPLICATION_DURABLE_IDENTITY_IMMUTABLE = "APPLICATION_DURABLE_IDENTITY_IMMUTABLE",
  PRIVACY_NOTICE_UNAVAILABLE = "PRIVACY_NOTICE_UNAVAILABLE",
  SCHEDULE_CONFLICT_CANDIDATE = "SCHEDULE_CONFLICT_CANDIDATE",
  SCHEDULE_CONFLICT_INTERVIEWER = "SCHEDULE_CONFLICT_INTERVIEWER",
  SCHEDULE_CONFLICT_ROOM = "SCHEDULE_CONFLICT_ROOM",
  LATEST_ROUND_REQUIRED = "LATEST_ROUND_REQUIRED",
  ROOT_ADMIN_PROTECTED = "ROOT_ADMIN_PROTECTED",
  IDENTITY_REBIND_FORBIDDEN = "IDENTITY_REBIND_FORBIDDEN",
  USER_INACTIVE = "USER_INACTIVE",
  UPLOAD_LIMIT_EXCEEDED = "UPLOAD_LIMIT_EXCEEDED",
  UNSUPPORTED_FILE_TYPE = "UNSUPPORTED_FILE_TYPE",
  MALWARE_SCAN_REQUIRED = "MALWARE_SCAN_REQUIRED",
  IDEMPOTENCY_REPLAY = "IDEMPOTENCY_REPLAY",
  INVALID_PERMISSION_DEPENDENCY = "INVALID_PERMISSION_DEPENDENCY",
  INTERNAL_ERROR = "INTERNAL_ERROR",
}

export type CommandError = {
  code: CommandErrorCode;
  message: string;
  details?: unknown;
};

export type CommandResult<T> =
  | { success: true; data: T }
  | { success: false; error: CommandError };

export type VerifiedActor = {
  authUserId: string;
  email: string;
  isActive: boolean;
  roles: string[];
  permissions: string[];
};

export type AuthorizationResult =
  | { authorized: true }
  | { authorized: false; reason?: string; code?: CommandErrorCode };

export type TrustedCommandDefinition<
  TRawInput,
  TTarget,
  TValidatedInput,
  TOutput,
> = {
  name: string;
  extractTarget?: (rawInput: TRawInput) => TTarget;
  authorize: (
    actor: VerifiedActor,
    target?: TTarget,
  ) => Promise<AuthorizationResult> | AuthorizationResult;
  validate: (
    rawInput: TRawInput,
  ) =>
    | { success: true; data: TValidatedInput }
    | { success: false; error: string; details?: unknown };
  execute: (actor: VerifiedActor, input: TValidatedInput) => Promise<TOutput>;
};
