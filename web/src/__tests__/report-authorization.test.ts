import assert from "node:assert/strict";
import test from "node:test";
import { isOwnWritableParticipant } from "@/lib/reports/authorization";

const OWN = "11111111-1111-4111-8111-111111111111";
const OTHER = "22222222-2222-4222-8222-222222222222";
const HISTORICAL = "33333333-3333-4333-8333-333333333333";
const FINAL = "44444444-4444-4444-8444-444444444444";

const rounds = [
  { interviewParticipantId: OWN, isCurrentRound: true, canEdit: true },
  { interviewParticipantId: HISTORICAL, isCurrentRound: false, canEdit: false },
  { interviewParticipantId: FINAL, isCurrentRound: true, canEdit: false },
] as const;

test("own-report boundary allows only the caller contextual current writable participant", () => {
  assert.equal(isOwnWritableParticipant(rounds, OWN), true);
  assert.equal(isOwnWritableParticipant(rounds, OTHER), false);
  assert.equal(isOwnWritableParticipant(rounds, HISTORICAL), false);
  assert.equal(isOwnWritableParticipant(rounds, FINAL), false);
});
