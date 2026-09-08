from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    file = Path(path)
    text = file.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: expected one match, found {count}: {old[:80]!r}")
    file.write_text(text.replace(old, new, 1), encoding="utf-8")


def replace_all(path: str, old: str, new: str, expected: int) -> None:
    file = Path(path)
    text = file.read_text(encoding="utf-8")
    count = text.count(old)
    if count != expected:
        raise RuntimeError(f"{path}: expected {expected} matches, found {count}: {old[:80]!r}")
    file.write_text(text.replace(old, new), encoding="utf-8")


# Harden the public server seam: validate untrusted enum/UUID/interval shapes before RPC.
path = "web/src/lib/commands/interview-lifecycle.ts"
replace_once(
    path,
    'const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;\n',
    'const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;\nconst SCHEDULE_STATUSES = new Set([\n  "AVAILABLE",\n  "SCHEDULED",\n  "AWAITING",\n  "CONFIRMED",\n  "CANCELLED",\n]);\n\nfunction optionalUuid(value: string | null): boolean {\n  return value === null || UUID.test(value);\n}\n'
)
replace_once(
    path,
    '  if (!UUID.test(input.interviewId) || !positiveVersion(input.expectedVersion))\n    return invalid("Interview hoặc version không hợp lệ.");\n  return withPermission(deps, ["interviews.status", "interviews.view"], (ctx) =>\n',
    '  if (\n    !UUID.test(input.interviewId) ||\n    !positiveVersion(input.expectedVersion) ||\n    !SCHEDULE_STATUSES.has(input.status)\n  )\n    return invalid("Interview, version hoặc trạng thái không hợp lệ.");\n  return withPermission(deps, ["interviews.status", "interviews.view"], (ctx) =>\n'
)
replace_once(
    path,
    '    !UUID.test(input.idempotencyKey) ||\n    !input.startAt ||\n    !input.endAt ||\n    !input.interviewFormatId\n',
    '    !UUID.test(input.idempotencyKey) ||\n    !input.startAt ||\n    !input.endAt ||\n    !input.interviewFormatId ||\n    !UUID.test(input.interviewFormatId) ||\n    !optionalUuid(input.roomId)\n'
)
replace_once(
    path,
    '    !positiveVersion(input.expectedTargetRoundVersion) ||\n    !input.participantAppUserIds.every((id) => UUID.test(id))\n  )\n    return invalid("Copy payload không hợp lệ.");\n',
    '    !positiveVersion(input.expectedTargetRoundVersion) ||\n    !input.participantAppUserIds.every((id) => UUID.test(id)) ||\n    !optionalUuid(input.interviewFormatId) ||\n    !optionalUuid(input.roomId) ||\n    (input.startAt === null) !== (input.endAt === null) ||\n    (input.startAt !== null && input.interviewFormatId === null)\n  )\n    return invalid("Copy payload không hợp lệ.");\n'
)

# Inactive Application/Interview is read-only except the matching Reactivate action.
path = "web/src/components/interview/InterviewDrawer.tsx"
replace_once(
    path,
    '  const [participantQuery, setParticipantQuery] = useState("");\n',
    '  const [participantQuery, setParticipantQuery] = useState("");\n  const [normalizationNotice, setNormalizationNotice] = useState<string | null>(null);\n'
)
replace_once(
    path,
    '  const scheduleValid =\n    (!startAt && !endAt) ||\n    Boolean(startIso && endIso && startIso < endIso && formatId);\n\n  return (\n',
    '  const scheduleValid =\n    (!startAt && !endAt) ||\n    Boolean(startIso && endIso && startIso < endIso && formatId);\n  const roundOperational = application.isActive && round.isActive;\n  const confirmed = round.scheduleStatus === "CONFIRMED";\n\n  return (\n'
)
replace_once(path, '        permissions.canManage ? (\n', '        permissions.canManage && roundOperational ? (\n')
replace_once(path, '        {permissions.canChangeStatus ? (\n', '        {permissions.canChangeStatus && roundOperational ? (\n')
replace_once(
    path,
    '      {!round.isActive && permissions.canManage ? (\n',
    '      {!round.isActive && application.isActive && permissions.canManage ? (\n'
)
replace_once(
    path,
    '      <fieldset\n        className="interview-form-grid"\n        disabled={!permissions.canManage || pending}\n      >\n',
    '      <fieldset\n        className="interview-form-grid"\n        disabled={!permissions.canManage || pending || !roundOperational}\n      >\n'
)
replace_once(
    path,
    '            onChange={(event) => {\n              const next = event.target.value;\n              setFormatId(next);\n              const format = formats.find((item) => item.id === next);\n              if (!format?.requiresRoom) setRoomId("");\n              if (!format?.requiresMeetingLink) setMeetingLink("");\n            }}\n',
    '            onChange={(event) => {\n              const next = event.target.value;\n              setFormatId(next);\n              const format = formats.find((item) => item.id === next);\n              const cleared: string[] = [];\n              if (!format?.requiresRoom && roomId) {\n                setRoomId("");\n                cleared.push("Phòng");\n              }\n              if (!format?.requiresMeetingLink && meetingLink) {\n                setMeetingLink("");\n                cleared.push("Meeting Link");\n              }\n              setNormalizationNotice(\n                cleared.length\n                  ? `${cleared.join(" và ")} đã được xóa vì không áp dụng cho hình thức mới.`\n                  : null,\n              );\n            }}\n'
)
replace_once(
    path,
    '        {selectedFormat?.requiresRoom ? (\n',
    '        {normalizationNotice ? (\n          <p className="interview-field-hint interview-form-span" role="status" aria-live="polite">\n            {normalizationNotice}\n          </p>\n        ) : null}\n        {selectedFormat?.requiresRoom ? (\n'
)
replace_once(
    path,
    '          <textarea\n            value={demoTopic}\n            onChange={(event) => setDemoTopic(event.target.value)}\n            rows={2}\n          />\n',
    '          <textarea\n            value={demoTopic}\n            onChange={(event) => setDemoTopic(event.target.value)}\n            rows={2}\n            disabled={confirmed}\n          />\n'
)
replace_once(
    path,
    '          <textarea\n            value={note}\n            onChange={(event) => setNote(event.target.value)}\n            rows={3}\n          />\n',
    '          <textarea\n            value={note}\n            onChange={(event) => setNote(event.target.value)}\n            rows={3}\n            disabled={confirmed}\n          />\n'
)
replace_once(
    path,
    '        </label>\n      </fieldset>\n\n      <section\n        className="interview-drawer-section"\n        aria-labelledby="participants-heading"\n',
    '        </label>\n        {confirmed ? (\n          <p className="interview-field-hint interview-form-span">\n            Lịch đã xác nhận chỉ cho phép xếp lại logistics bằng lệnh Reschedule. Đổi status khác trước khi sửa Demo Topic hoặc Interview Note.\n          </p>\n        ) : null}\n      </fieldset>\n\n      {!application.isActive ? (\n        <section className="interview-drawer-section">\n          <h3>Application không hoạt động</h3>\n          <p>Reactivate Application từ dòng Application trước khi thực hiện mutation trên Interview.</p>\n        </section>\n      ) : null}\n\n      <section\n        className="interview-drawer-section"\n        aria-labelledby="participants-heading"\n'
)
replace_all(
    path,
    '                {permissions.canManageParticipants ? (\n',
    '                {permissions.canManageParticipants && roundOperational ? (\n',
    1,
)
replace_once(
    path,
    '        {permissions.canManageParticipants ? (\n          <div className="interview-add-participant">\n',
    '        {permissions.canManageParticipants && roundOperational ? (\n          <div className="interview-add-participant">\n'
)
replace_once(
    path,
    '        {removedParticipants.length && permissions.canManageParticipants ? (\n',
    '        {removedParticipants.length && permissions.canManageParticipants && roundOperational ? (\n'
)

# Copy draft: enforce paired intervals and drop no-longer-active source participants from prefill visibly.
path = "web/src/components/interview/InterviewDialogs.tsx"
replace_once(
    path,
    '  const [participantIds, setParticipantIds] = useState<string[]>(\n    sourceRound.participants\n      .filter((p) => p.isCurrent)\n      .sort((a, b) => a.order - b.order)\n      .map((p) => p.appUserId),\n  );\n',
    '  const [participantIds, setParticipantIds] = useState<string[]>(\n    sourceRound.participants\n      .filter((p) => p.isCurrent && users.some((user) => user.id === p.appUserId))\n      .sort((a, b) => a.order - b.order)\n      .map((p) => p.appUserId),\n  );\n  const [normalizationNotice, setNormalizationNotice] = useState<string | null>(null);\n'
)
replace_once(
    path,
    '  const canSubmit = Boolean(\n    target &&\n      (!startAt || (startIso && endIso && startIso < endIso && formatId)),\n  );\n',
    '  const scheduleEmpty = !startAt && !endAt;\n  const scheduleComplete = Boolean(\n    startAt && endAt && startIso && endIso && startIso < endIso && formatId,\n  );\n  const canSubmit = Boolean(target && (scheduleEmpty || scheduleComplete));\n  const inactivePrefillParticipants = sourceRound.participants.filter(\n    (participant) =>\n      participant.isCurrent && !users.some((user) => user.id === participant.appUserId),\n  );\n'
)
replace_once(
    path,
    '          <Button\n            onClick={async () => setTargets(await onSearchApplications(query))}\n          >\n',
    '          <Button\n            disabled={pending}\n            onClick={async () => setTargets(await onSearchApplications(query))}\n          >\n'
)
replace_once(
    path,
    '              onChange={(event) => {\n                const value = event.target.value;\n                setFormatId(value);\n                const format = formats.find((item) => item.id === value);\n                if (!format?.requiresRoom) setRoomId("");\n                if (!format?.requiresMeetingLink) setMeetingLink("");\n              }}\n',
    '              onChange={(event) => {\n                const value = event.target.value;\n                setFormatId(value);\n                const format = formats.find((item) => item.id === value);\n                const cleared: string[] = [];\n                if (!format?.requiresRoom && roomId) {\n                  setRoomId("");\n                  cleared.push("Phòng");\n                }\n                if (!format?.requiresMeetingLink && meetingLink) {\n                  setMeetingLink("");\n                  cleared.push("Meeting Link");\n                }\n                setNormalizationNotice(\n                  cleared.length\n                    ? `${cleared.join(" và ")} đã được xóa vì không áp dụng cho hình thức mới.`\n                    : null,\n                );\n              }}\n'
)
replace_once(
    path,
    '          {selectedFormat?.requiresRoom ? (\n',
    '          {normalizationNotice ? (\n            <p className="interview-field-hint interview-form-span" role="status" aria-live="polite">\n              {normalizationNotice}\n            </p>\n          ) : null}\n          {selectedFormat?.requiresRoom ? (\n'
)
replace_once(
    path,
    '        <fieldset className="interview-copy-participants">\n',
    '        {inactivePrefillParticipants.length ? (\n          <div className="ui-alert ui-alert--warning" role="status">\n            {inactivePrefillParticipants.map((participant) => participant.name).join(", ")} không còn Active nên không được prefill vào Copy. Hãy chọn Participant Active thay thế nếu cần.\n          </div>\n        ) : null}\n        <fieldset className="interview-copy-participants">\n'
)

# Table/toolbar mutation affordances obey latest/active gates instead of relying on server rejection for obvious state.
path = "web/src/components/interview/InterviewPage.tsx"
replace_once(
    path,
    'function latestRound(group: InterviewApplicationGroup): InterviewRound | null {\n  return [...group.rounds].sort((a, b) => b.roundNo - a.roundNo)[0] ?? null;\n}\n',
    'function latestRound(group: InterviewApplicationGroup): InterviewRound | null {\n  return [...group.rounds].sort((a, b) => b.roundNo - a.roundNo)[0] ?? null;\n}\n\nfunction canCreateNextRound(group: InterviewApplicationGroup): boolean {\n  const latest = latestRound(group);\n  return Boolean(\n    group.isActive && latest?.isActive && latest.reportStatus !== "HIRED",\n  );\n}\n\nfunction isLatestRound(\n  group: InterviewApplicationGroup,\n  round: InterviewRound,\n): boolean {\n  return latestRound(group)?.interviewId === round.interviewId;\n}\n'
)
replace_once(
    path,
    '  const renderStatus = (round: InterviewRound) =>\n    data.permissions.canChangeStatus ? (\n',
    '  const renderStatus = (round: InterviewRound, interactive = true) =>\n    interactive && data.permissions.canChangeStatus ? (\n'
)
replace_once(
    path,
    '            disabled={busy || !selected.application.isActive}\n',
    '            disabled={busy || !canCreateNextRound(selected.application)}\n'
)
replace_once(
    path,
    '        {data.permissions.canManage && selected ? (\n          <Button\n            variant="danger"\n',
    '        {data.permissions.canManage &&\n        selected &&\n        selected.application.isActive &&\n        selected.round.isActive &&\n        isLatestRound(selected.application, selected.round) ? (\n          <Button\n            variant="danger"\n'
)
replace_once(
    path,
    '        {data.permissions.canChangeStatus && selected ? (\n',
    '        {data.permissions.canChangeStatus &&\n        selected &&\n        selected.application.isActive &&\n        selected.round.isActive ? (\n'
)
replace_once(
    path,
    '  renderStatus: (round: InterviewRound) => React.ReactNode;\n',
    '  renderStatus: (round: InterviewRound, interactive?: boolean) => React.ReactNode;\n'
)
replace_once(
    path,
    '        <td data-label="Trạng thái">{latest ? renderStatus(latest) : "—"}</td>\n',
    '        <td data-label="Trạng thái">\n          {latest\n            ? renderStatus(latest, application.isActive && latest.isActive)\n            : "—"}\n        </td>\n'
)
replace_once(
    path,
    '            {canManage && application.isActive ? (\n              <Button variant="ghost" disabled={busy} onClick={onCreateNext}>\n',
    '            {canManage && canCreateNextRound(application) ? (\n              <Button variant="ghost" disabled={busy} onClick={onCreateNext}>\n'
)
replace_once(
    path,
    '              <td data-label="Trạng thái">{renderStatus(round)}</td>\n',
    '              <td data-label="Trạng thái">\n                {renderStatus(round, application.isActive && round.isActive)}\n              </td>\n'
)
replace_once(
    path,
    '                  {canManage ? (\n                    <Button\n                      variant="ghost"\n                      onClick={() => onCopy(round.interviewId)}\n',
    '                  {canManage && application.isActive && round.isActive ? (\n                    <Button\n                      variant="ghost"\n                      onClick={() => onCopy(round.interviewId)}\n'
)

# Focused regression coverage for the repaired public seam.
path = "web/src/__tests__/interview-commands.test.ts"
replace_once(
    path,
    '  reorderInterviewParticipants,\n  saveInterviewSchedule,\n} from "@/lib/commands/interview-lifecycle";\n',
    '  reorderInterviewParticipants,\n  saveInterviewSchedule,\n  changeInterviewScheduleStatus,\n  rescheduleConfirmedInterview,\n} from "@/lib/commands/interview-lifecycle";\n'
)
append = r'''

test("public server seam rejects malformed status and half-filled copy interval before RPC", async () => {
  const { client, calls } = rpcRecorder();
  const resolveSession = async () => session(["interviews.view", "interviews.status", "interviews.manage"]);
  const badStatus = await changeInterviewScheduleStatus(
    { interviewId: ids.interview, status: "NOT_A_STATUS", expectedVersion: 2 },
    { client, resolveSession },
  );
  assert.equal(badStatus.success, false);
  const halfCopy = await copyInterviewSchedule(
    {
      sourceInterviewId: ids.interview,
      targetApplicationId: ids.application,
      expectedSourceVersion: 5,
      expectedTargetApplicationVersion: 7,
      expectedTargetRoundId: ids.targetRound,
      expectedTargetRoundVersion: 3,
      startAt: "2026-05-20T07:00:00.000Z",
      endAt: null,
      interviewFormatId: ids.format,
      roomId: null,
      meetingLink: null,
      interviewNote: null,
      participantAppUserIds: [ids.user],
      idempotencyKey: ids.key,
    },
    { client, resolveSession },
  );
  assert.equal(halfCopy.success, false);
  assert.equal(calls.length, 0);
});

test("confirmed reschedule rejects non-UUID format identifiers before RPC", async () => {
  const { client, calls } = rpcRecorder();
  const result = await rescheduleConfirmedInterview(
    {
      interviewId: ids.interview,
      startAt: "2026-05-20T07:00:00.000Z",
      endAt: "2026-05-20T08:30:00.000Z",
      interviewFormatId: "not-a-uuid",
      roomId: null,
      meetingLink: null,
      expectedVersion: 2,
      idempotencyKey: ids.key,
    },
    { client, resolveSession: async () => session(["interviews.manage"]) },
  );
  assert.equal(result.success, false);
  assert.equal(calls.length, 0);
});
'''
file = Path(path)
text = file.read_text(encoding="utf-8")
if 'public server seam rejects malformed status' in text:
    raise RuntimeError("focused regression tests already present")
file.write_text(text.rstrip() + append + "\n", encoding="utf-8")

print("S04 self-review repair applied")
