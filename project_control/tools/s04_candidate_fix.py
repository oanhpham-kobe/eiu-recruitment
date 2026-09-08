from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, text: str) -> None:
    (ROOT / path).write_text(text.rstrip() + "\n", encoding="utf-8")


def once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)

# Server-derived permission surface.
p = "web/src/lib/interview/server.ts"
t = read(p)
t = once(
    t,
    '    canReactivateApplication: root || has(session, "applications.manage"),\n  };',
    '    canReactivateApplication: root || has(session, "applications.manage"),\n'
    '    canDeleteApplication:\n'
    '      root ||\n'
    '      has(session, "applications.delete") ||\n'
    '      has(session, "applications.manage"),\n'
    '  };',
    "server delete application permission",
)
write(p, t)

# Avoid TS lib-specific Intl alias; the runtime part discriminator is a string.
for p in [
    "web/src/components/interview/InterviewDrawer.tsx",
    "web/src/components/interview/InterviewDialogs.tsx",
]:
    t = read(p)
    if "Intl.DateTimeFormatPartTypes" not in t:
        raise SystemExit(f"Intl type anchor missing: {p}")
    t = t.replace("Intl.DateTimeFormatPartTypes", "string")
    write(p, t)

# Searchable participant selection in the existing drawer.
p = "web/src/components/interview/InterviewDrawer.tsx"
t = read(p)
t = once(
    t,
    '  const [participantUserId, setParticipantUserId] = useState("");',
    '  const [participantUserId, setParticipantUserId] = useState("");\n'
    '  const [participantQuery, setParticipantQuery] = useState("");',
    "participant query state",
)
t = once(
    t,
    '  const selectableUsers = users.filter((user) => !currentUserIds.has(user.id));',
    '  const normalizedParticipantQuery = participantQuery.trim().toLocaleLowerCase("vi");\n'
    '  const selectableUsers = users.filter((user) => {\n'
    '    if (currentUserIds.has(user.id)) return false;\n'
    '    if (!normalizedParticipantQuery) return true;\n'
    '    return `${user.name} ${user.email} ${user.jobTitle ?? ""}`\n'
    '      .toLocaleLowerCase("vi")\n'
    '      .includes(normalizedParticipantQuery);\n'
    '  });',
    "participant filter",
)
t = once(
    t,
    '          <div className="interview-add-participant">\n            <label>\n              Thêm người đang hoạt động',
    '          <div className="interview-add-participant">\n'
    '            <label>\n'
    '              Tìm người tham dự\n'
    '              <input\n'
    '                type="search"\n'
    '                value={participantQuery}\n'
    '                onChange={(event) => setParticipantQuery(event.target.value)}\n'
    '                autoComplete="off"\n'
    '              />\n'
    '            </label>\n'
    '            <label>\n'
    '              Thêm người đang hoạt động',
    "participant search control",
)
write(p, t)

# Exact Submission selector as a structured accessible listbox rather than a lossy one-line native option.
p = "web/src/components/interview/InterviewDialogs.tsx"
t = read(p)
old = '''        <label>\n          Phiếu ứng tuyển cụ thể\n          <select value={submissionId} onChange={(event) => setSubmissionId(event.target.value)}>\n            <option value="">Chọn Phiếu</option>\n            {submissions.map((option) => (\n              <option key={option.submissionId} value={option.submissionId}>\n                {option.candidateName} — {option.verifiedEmail} — {new Date(option.submittedAt).toLocaleString("vi-VN", { timeZone: "Asia/Ho_Chi_Minh" })} — {option.status}\n              </option>\n            ))}\n          </select>\n          <span className="interview-field-hint">Không tự suy ra Phiếu mới nhất.</span>\n        </label>'''
new = '''        <div className="interview-submission-selector">\n          <strong id="submission-selector-label">Phiếu ứng tuyển cụ thể</strong>\n          <div\n            className="interview-submission-options"\n            role="listbox"\n            aria-labelledby="submission-selector-label"\n          >\n            {submissions.map((option) => (\n              <button\n                key={option.submissionId}\n                type="button"\n                role="option"\n                aria-selected={submissionId === option.submissionId}\n                className="interview-submission-option"\n                onClick={() => setSubmissionId(option.submissionId)}\n              >\n                <strong>{option.candidateName}</strong>\n                <span>{option.verifiedEmail}</span>\n                <span>\n                  Phiếu: {new Date(option.submittedAt).toLocaleString("vi-VN", { timeZone: "Asia/Ho_Chi_Minh" })} · {option.status}\n                </span>\n              </button>\n            ))}\n          </div>\n          <span className="interview-field-hint">Không tự suy ra Phiếu mới nhất.</span>\n        </div>'''
t = once(t, old, new, "structured submission selector")
write(p, t)

# Page state, create-next confirmation, permission split, and duplicate-id cleanup.
p = "web/src/components/interview/InterviewPage.tsx"
t = read(p)
t = once(
    t,
    'export function InterviewPage({ initialData }: { initialData: InterviewPageData }) {\n'
    '  const [data, setData] = useState(initialData);\n'
    '  const [filters, setFilters] = useState<InterviewPageFilters>(INITIAL_INTERVIEW_FILTERS);',
    'export function InterviewPage({\n'
    '  initialData,\n'
    '  initialActivity = "ACTIVE",\n'
    '}: {\n'
    '  initialData: InterviewPageData;\n'
    '  initialActivity?: InterviewPageFilters["activity"];\n'
    '}) {\n'
    '  const [data, setData] = useState(initialData);\n'
    '  const [filters, setFilters] = useState<InterviewPageFilters>({\n'
    '    ...INITIAL_INTERVIEW_FILTERS,\n'
    '    activity: initialActivity,\n'
    '  });',
    "initial activity state",
)
t = once(
    t,
    '  const searchSubmissions = useCallback(async (query: string): Promise<SubmissionSelectorOption[]> => {',
    '  const requestCreateNextRound = (application: InterviewApplicationGroup) => {\n'
    '    setConfirmState({\n'
    '      title: "Tạo vòng phỏng vấn tiếp theo",\n'
    '      message:\n'
    '        "Server sẽ kiểm tra vòng mới nhất còn Active và chưa HIRED. Demo Topic của vòng mới luôn để trống.",\n'
    '      execute: async () => {\n'
    '        await createNextRound(application);\n'
    '      },\n'
    '    });\n'
    '  };\n\n'
    '  const searchSubmissions = useCallback(async (query: string): Promise<SubmissionSelectorOption[]> => {',
    "create next confirmation helper",
)
t = once(
    t,
    '          <Button disabled={busy || !selected.application.isActive} onClick={() => void createNextRound(selected.application)}>Tạo vòng tiếp theo</Button>',
    '          <Button disabled={busy || !selected.application.isActive} onClick={() => requestCreateNextRound(selected.application)}>Tạo vòng tiếp theo</Button>',
    "toolbar create next confirmation",
)
t = once(
    t,
    '                  canReactivateApplication={data.permissions.canReactivateApplication}\n',
    '                  canReactivateApplication={data.permissions.canReactivateApplication}\n'
    '                  canDeleteApplication={data.permissions.canDeleteApplication}\n',
    "pass delete permission",
)
t = once(
    t,
    '                  onCreateNext={() => void createNextRound(application)}',
    '                  onCreateNext={() => requestCreateNextRound(application)}',
    "row create next confirmation",
)
t = once(
    t,
    '  canReactivateApplication,\n  renderStatus,',
    '  canReactivateApplication,\n  canDeleteApplication,\n  renderStatus,',
    "rows delete permission destructure",
)
t = once(
    t,
    '  canReactivateApplication: boolean;\n  renderStatus:',
    '  canReactivateApplication: boolean;\n  canDeleteApplication: boolean;\n  renderStatus:',
    "rows delete permission type",
)
t = once(
    t,
    '{canReactivateApplication ? <Button variant="ghost" disabled={busy} onClick={onDeleteApplication}>Xóa App</Button> : null}',
    '{canDeleteApplication ? <Button variant="ghost" disabled={busy} onClick={onDeleteApplication}>Xóa App</Button> : null}',
    "delete permission use",
)
t = once(
    t,
    ' aria-controls={`rounds-${application.applicationId}`}',
    '',
    "remove non-container aria-controls",
)
t = once(
    t,
    ' id={`rounds-${application.applicationId}`}',
    '',
    "remove duplicate round id",
)
write(p, t)

# Preserve the non-sensitive activity filter when the server rendered it from URL state.
p = "web/src/app/interviews/page.tsx"
t = read(p)
t = once(
    t,
    '    return <InterviewPage initialData={data} />;',
    '    return <InterviewPage initialData={data} initialActivity={activity} />;',
    "server initial activity",
)
write(p, t)

# Permission-aware Interview nav on both desktop and mobile.
p = "web/src/components/shell/Sidebar.tsx"
t = read(p)
t = once(
    t,
    '  navItems?: NavItem[];\n}',
    '  navItems?: NavItem[];\n  showInterviews?: boolean;\n}',
    "sidebar show interviews prop",
)
t = once(
    t,
    '  navItems = DEFAULT_NAV_ITEMS,\n}: SidebarProps) {\n  return (',
    '  navItems = DEFAULT_NAV_ITEMS,\n  showInterviews = true,\n}: SidebarProps) {\n  const visibleNavItems = navItems.filter(\n    (item) => item.href !== "/interviews" || showInterviews,\n  );\n  return (',
    "sidebar visible items",
)
t = once(t, '          {navItems.map((item) => {', '          {visibleNavItems.map((item) => {', "sidebar map")
write(p, t)

p = "web/src/components/shell/MobileNavigation.tsx"
t = read(p)
t = once(
    t,
    '  currentPath: string;\n  onClose: () => void;',
    '  currentPath: string;\n  showInterviews?: boolean;\n  onClose: () => void;',
    "mobile nav prop type",
)
t = once(
    t,
    '  currentPath,\n  onClose,\n}: MobileNavigationProps) {',
    '  currentPath,\n  showInterviews = true,\n  onClose,\n}: MobileNavigationProps) {',
    "mobile nav prop",
)
t = once(
    t,
    '            {DEFAULT_NAV_ITEMS.map((item) => (',
    '            {DEFAULT_NAV_ITEMS.filter(\n'
    '              (item) => item.href !== "/interviews" || showInterviews,\n'
    '            ).map((item) => (',
    "mobile nav filter",
)
write(p, t)

p = "web/src/components/shell/AppShell.tsx"
t = read(p)
t = once(
    t,
    '  currentPath?: string;\n}',
    '  currentPath?: string;\n  showInterviews?: boolean;\n}',
    "app shell prop type",
)
t = once(
    t,
    '  currentPath = "/",\n}: AppShellProps) {',
    '  currentPath = "/",\n  showInterviews = true,\n}: AppShellProps) {',
    "app shell prop",
)
t = once(t, '<Sidebar currentPath={currentPath} />', '<Sidebar currentPath={currentPath} showInterviews={showInterviews} />', "desktop nav permission")
t = once(
    t,
    '        currentPath={currentPath}\n        onClose={() => setMobileNavOpen(false)}',
    '        currentPath={currentPath}\n        showInterviews={showInterviews}\n        onClose={() => setMobileNavOpen(false)}',
    "mobile nav permission",
)
write(p, t)

p = "web/src/app/layout.tsx"
t = read(p)
t = once(
    t,
    'import { CandidateShell } from "@/components/shell/CandidateShell";\nimport "./globals.css";',
    'import { CandidateShell } from "@/components/shell/CandidateShell";\n'
    'import { getServerSession } from "@/lib/auth/session";\n'
    'import { createServerClient } from "@/lib/supabase/server";\n'
    'import "./globals.css";',
    "layout session imports",
)
t = once(
    t,
    '  const shellKind = resolveShellKind(pathname);\n\n  const content =',
    '  const shellKind = resolveShellKind(pathname);\n'
    '  let showInterviews = false;\n'
    '  if (shellKind === "internal") {\n'
    '    const session = await getServerSession(await createServerClient());\n'
    '    showInterviews = Boolean(\n'
    '      session.user?.roles.includes("ROOT_ADMIN") ||\n'
    '        session.user?.permissions.includes("interviews.view"),\n'
    '    );\n'
    '  }\n\n'
    '  const content =',
    "layout permission resolution",
)
t = once(
    t,
    '      <AppShell currentPath={pathname}>{children}</AppShell>',
    '      <AppShell currentPath={pathname} showInterviews={showInterviews}>\n'
    '        {children}\n'
    '      </AppShell>',
    "layout nav permission",
)
write(p, t)

# CSS: no hidden design-token aliases or !important shortcuts; add structured selector styling.
p = "web/src/styles/interview.css"
t = read(p)
t = t.replace(" !important", "")
if ".interview-submission-options" not in t:
    t += '''\n\n.interview-submission-selector {\n  display: grid;\n  gap: var(--space-2);\n}\n\n.interview-submission-options {\n  display: grid;\n  gap: var(--space-2);\n  max-height: 320px;\n  overflow: auto;\n  padding: var(--space-2);\n  border: 1px solid var(--line);\n  border-radius: var(--radius-control);\n  background: var(--canvas);\n}\n\n.interview-submission-option {\n  min-height: 72px;\n  display: grid;\n  gap: 2px;\n  width: 100%;\n  padding: 10px 12px;\n  border: 1px solid var(--line);\n  border-radius: var(--radius-control);\n  background: var(--surface);\n  color: var(--ink-950);\n  font: inherit;\n  font-size: 16px;\n  text-align: left;\n  cursor: pointer;\n}\n\n.interview-submission-option[aria-selected="true"] {\n  border-color: var(--eiu-blue);\n  box-shadow: 0 0 0 2px var(--status-info-bg);\n}\n\n.interview-submission-option span {\n  color: var(--ink-600);\n}\n'''
write(p, t)

# Extend focused command contract coverage.
p = "web/src/__tests__/interview-commands.test.ts"
t = read(p)
t = once(
    t,
    '  reactivateApplication,\n  reorderInterviewParticipants,',
    '  reactivateApplication,\n  readdInterviewParticipant,\n  removeInterviewParticipant,\n  reorderInterviewParticipants,',
    "participant command test imports",
)
if 'same intended retry keeps the same caller-owned key' not in t:
    t += '''\n\ntest("same intended retry keeps the same caller-owned key for create-next and Save Copy", async () => {\n  const { client, calls } = rpcRecorder();\n  const manage = async () => session(["interviews.manage", "interviews.view"]);\n  const createInput = { applicationId: ids.application, idempotencyKey: ids.key };\n  await createNextInterviewRound(createInput, { client, resolveSession: manage });\n  await createNextInterviewRound(createInput, { client, resolveSession: manage });\n  assert.equal(calls[0]?.args.p_idempotency_key, ids.key);\n  assert.equal(calls[1]?.args.p_idempotency_key, ids.key);\n\n  const copyInput = {\n    sourceInterviewId: ids.interview,\n    targetApplicationId: ids.application,\n    expectedSourceVersion: 5,\n    expectedTargetApplicationVersion: 7,\n    expectedTargetRoundId: ids.targetRound,\n    expectedTargetRoundVersion: 3,\n    startAt: null,\n    endAt: null,\n    interviewFormatId: null,\n    roomId: null,\n    meetingLink: null,\n    interviewNote: null,\n    participantAppUserIds: [ids.user],\n    idempotencyKey: ids.key,\n  };\n  await copyInterviewSchedule(copyInput, { client, resolveSession: manage });\n  await copyInterviewSchedule(copyInput, { client, resolveSession: manage });\n  assert.equal(calls[2]?.args.p_idempotency_key, ids.key);\n  assert.equal(calls[3]?.args.p_idempotency_key, ids.key);\n});\n\ntest("remove and re-add forward the repaired S04-005 arguments exactly", async () => {\n  const { client, calls } = rpcRecorder();\n  const resolveSession = async () => session(["interviews.view", "interviews.participants"]);\n  await removeInterviewParticipant(\n    { interviewParticipantId: ids.participant, expectedVersion: 8 },\n    { client, resolveSession },\n  );\n  await readdInterviewParticipant(\n    {\n      interviewParticipantId: ids.participant,\n      restoreMode: "RESTORE_OLD_REPORT",\n      idempotencyKey: ids.key,\n    },\n    { client, resolveSession },\n  );\n  assert.deepEqual(calls[0], {\n    name: "remove_interview_participant",\n    args: {\n      p_interview_participant_id: ids.participant,\n      p_expected_version: 8,\n    },\n  });\n  assert.deepEqual(calls[1], {\n    name: "readd_interview_participant",\n    args: {\n      p_interview_participant_id: ids.participant,\n      p_restore_mode: "RESTORE_OLD_REPORT",\n      p_idempotency_key: ids.key,\n    },\n  });\n});\n\ntest("Application Reactivate exposes stable structured owner, participant and conflict errors", async () => {\n  const codes = [\n    "STALE_VERSION",\n    "ACTIVE_APPLICATION_OWNER_REASSIGN_REQUIRED",\n    "CURRENT_PARTICIPANT_INACTIVE_REASSIGN_REQUIRED",\n    "SCHEDULE_CONFLICT_CANDIDATE",\n    "SCHEDULE_CONFLICT_ROOM",\n    "SCHEDULE_CONFLICT_INTERVIEWER",\n  ];\n  for (const code of codes) {\n    const client = {\n      rpc: async () => ({ data: { success: false, error_code: code }, error: null }),\n    } as unknown as SupabaseClient;\n    const result = await reactivateApplication(\n      { applicationId: ids.application, expectedVersion: 6 },\n      { client, resolveSession: async () => session(["applications.manage"]) },\n    );\n    assert.equal(result.success, false);\n    if (!result.success) {\n      assert.equal(result.error.code, code);\n      assert.doesNotMatch(result.error.message, /sql|postgres|function public/i);\n    }\n  }\n});\n'''
write(p, t)

# Copy RPC requires both manage and view; fail locally before the RPC when either is missing.
p = "web/src/lib/commands/interview-lifecycle.ts"
t = read(p)
t = once(
    t,
    '  return withPermission(deps, ["interviews.manage"], (ctx) =>\n    executeRpc(ctx, "copy_interview_schedule", {',
    '  return withPermission(deps, ["interviews.manage", "interviews.view"], (ctx) =>\n    executeRpc(ctx, "copy_interview_schedule", {',
    "copy permission contract",
)
write(p, t)

print("S04 focused candidate fixes applied")
