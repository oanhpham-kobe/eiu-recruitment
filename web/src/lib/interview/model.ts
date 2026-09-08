export type InterviewActivityFilter = "ACTIVE" | "INACTIVE" | "ALL";
export type InterviewScheduleStatus =
  | "AVAILABLE"
  | "SCHEDULED"
  | "AWAITING"
  | "CONFIRMED"
  | "CANCELLED";

export const INTERVIEW_STATUS_LABEL: Record<InterviewScheduleStatus, string> = {
  AVAILABLE: "Sẵn sàng",
  SCHEDULED: "Đã xếp lịch",
  AWAITING: "Chờ xác nhận",
  CONFIRMED: "Đã xác nhận",
  CANCELLED: "Hủy",
};

export const INTERVIEW_COLUMNS = [48, 340, 250, 220, 170, 360, 92] as const;

export interface InterviewParticipant {
  interviewParticipantId: string;
  appUserId: string;
  order: number;
  name: string;
  email: string;
  jobTitle: string | null;
  isCurrent: boolean;
  removedAt: string | null;
  versionNo: number;
  hasReportHistory: boolean;
}

export interface InterviewRound {
  interviewId: string;
  applicationId: string;
  roundNo: number;
  demoTopic: string | null;
  startAt: string | null;
  endAt: string | null;
  interviewFormatId: string | null;
  roomId: string | null;
  meetingLink: string | null;
  scheduleStatus: InterviewScheduleStatus;
  reportStatus: string;
  interviewNote: string | null;
  isActive: boolean;
  versionNo: number;
  updatedAt: string;
  participants: InterviewParticipant[];
}

export interface InterviewApplicationGroup {
  applicationId: string;
  submissionId: string;
  candidateId: string;
  candidateName: string;
  candidateEmail: string;
  candidatePhone: string;
  submissionDate: string;
  submissionStatus: string;
  unitId: string;
  unitName: string;
  departmentTeamId: string | null;
  departmentTeamName: string | null;
  positionId: string;
  positionName: string;
  hrOwnerId: string;
  hrOwnerName: string;
  isActive: boolean;
  versionNo: number;
  rounds: InterviewRound[];
}

export interface InterviewFormatOption {
  id: string;
  code: string;
  name: string;
  requiresRoom: boolean;
  requiresMeetingLink: boolean;
  isActive: boolean;
}

export interface InterviewRoomOption {
  id: string;
  code: string | null;
  name: string;
  building: string | null;
  isActive: boolean;
}

export interface InterviewUserOption {
  id: string;
  name: string;
  email: string;
  jobTitle: string | null;
}

export interface SubmissionSelectorOption {
  submissionId: string;
  candidateName: string;
  verifiedEmail: string;
  submittedAt: string;
  status: string;
}

export interface ApplicationSelectorOption {
  applicationId: string;
  label: string;
  candidateName: string;
  candidateEmail: string;
  versionNo: number;
  latestRoundId: string;
  latestRoundVersionNo: number;
  latestRoundNo: number;
}

export interface InterviewPermissions {
  canView: boolean;
  canManage: boolean;
  canChangeStatus: boolean;
  canManageParticipants: boolean;
  canCreateApplication: boolean;
  canReactivateApplication: boolean;
  canDeleteApplication: boolean;
}

export interface InterviewPageFilters {
  query: string;
  activity: InterviewActivityFilter;
}

export interface InterviewPageData {
  groups: InterviewApplicationGroup[];
  page: number;
  pageCount: number;
  formats: InterviewFormatOption[];
  rooms: InterviewRoomOption[];
  participantUsers: InterviewUserOption[];
  permissions: InterviewPermissions;
}

export const INITIAL_INTERVIEW_FILTERS: InterviewPageFilters = {
  query: "",
  activity: "ACTIVE",
};

export function normalizeInterviewFilters(
  value: Partial<InterviewPageFilters> | undefined,
): InterviewPageFilters {
  const activity =
    value?.activity === "INACTIVE" || value?.activity === "ALL"
      ? value.activity
      : "ACTIVE";
  return {
    query:
      typeof value?.query === "string" ? value.query.trim().slice(0, 256) : "",
    activity,
  };
}

export function nextExpandedApplicationId(
  currentId: string | null,
  clickedId: string,
): string | null {
  return currentId === clickedId ? null : clickedId;
}

export function formatInterviewTime(
  startAt: string | null,
  endAt: string | null,
  locale: "vi" | "en" = "vi",
): string {
  if (!startAt || !endAt) return "Chưa xếp lịch";
  const start = new Date(startAt);
  const end = new Date(endAt);
  const language = locale === "en" ? "en-GB" : "vi-VN";
  const time = new Intl.DateTimeFormat(language, {
    timeZone: "Asia/Ho_Chi_Minh",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
  const date = new Intl.DateTimeFormat(language, {
    timeZone: "Asia/Ho_Chi_Minh",
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
  return `${time.format(start)} – ${time.format(end)} · ${date.format(start)}`;
}
