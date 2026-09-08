import type { InterviewerReportRound } from "./model";

type WritableRoundContext = Pick<
  InterviewerReportRound,
  "interviewParticipantId" | "isCurrentRound" | "canEdit"
>;

export function isOwnWritableParticipant(
  rounds: readonly WritableRoundContext[],
  interviewParticipantId: string,
): boolean {
  return rounds.some(
    (round) =>
      round.interviewParticipantId === interviewParticipantId &&
      round.isCurrentRound &&
      round.canEdit,
  );
}
