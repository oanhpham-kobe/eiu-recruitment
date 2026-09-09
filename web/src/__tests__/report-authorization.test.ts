import assert from "node:assert/strict";
import test from "node:test";
import { isOwnWritableParticipant } from "@/lib/reports/authorization";

const OWN = "11111111-1111-4111-8111-111111111111";
const OTHER = "22222222-2222-4222-8222-222222222222";
const HISTORICAL = "33333333-3333-4333-8333-333333333333";
const FINAL = "44444444-4444-4444-8444-444444444444";

const contextualRounds = [
  { interviewParticipantId: OWN, isCurrentRound: true, canEdit: true },
  { interviewParticipantId: HISTORICAL, isCurrentRound: false, canEdit: false },
  { interviewParticipantId: FINAL, isCurrentRound: true, canEdit: false },
] as const;

test("own-report boundary allows only the caller contextual current writable participant", () => {
  assert.equal(isOwnWritableParticipant(contextualRounds, OWN), true);
});

test("broader HR or Root authority cannot make other, historical, or final targets writable", () => {
  // The own-report action deliberately ignores global HR/Root permissions here.
  // Its only write authority is the caller-specific contextual read projection.
  assert.equal(isOwnWritableParticipant(contextualRounds, OTHER), false);
  assert.equal(isOwnWritableParticipant(contextualRounds, HISTORICAL), false);
  assert.equal(isOwnWritableParticipant(contextualRounds, FINAL), false);
});
