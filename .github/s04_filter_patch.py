from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    file = Path(path)
    text = file.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: expected one match, found {count}: {old[:100]!r}")
    file.write_text(text.replace(old, new, 1), encoding="utf-8")


# ---- model: complete canonical filter state and filter reference options ----
path = "web/src/lib/interview/model.ts"
replace_once(
    path,
    '''export interface InterviewPageFilters {
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
''',
    '''export interface InterviewFilterUnitOption {
  id: string;
  name: string;
}

export interface InterviewFilterTeamOption extends InterviewFilterUnitOption {
  unitId: string;
}

export interface InterviewFilterPositionOption extends InterviewFilterUnitOption {
  unitId: string;
  departmentTeamId: string | null;
}

export interface InterviewPageFilters {
  query: string;
  activity: InterviewActivityFilter;
  unitId: string;
  departmentTeamId: string;
  positionId: string;
  scheduleStatus: InterviewScheduleStatus | "";
  dateFrom: string;
  dateTo: string;
  location: string;
  interviewFormatId: string;
  participantAppUserId: string;
  hrOwnerId: string;
}

export interface InterviewPageData {
  groups: InterviewApplicationGroup[];
  page: number;
  pageCount: number;
  formats: InterviewFormatOption[];
  rooms: InterviewRoomOption[];
  participantUsers: InterviewUserOption[];
  filterUnits: InterviewFilterUnitOption[];
  filterTeams: InterviewFilterTeamOption[];
  filterPositions: InterviewFilterPositionOption[];
  filterHrOwners: InterviewUserOption[];
  permissions: InterviewPermissions;
}

export const INITIAL_INTERVIEW_FILTERS: InterviewPageFilters = {
  query: "",
  activity: "ACTIVE",
  unitId: "",
  departmentTeamId: "",
  positionId: "",
  scheduleStatus: "",
  dateFrom: "",
  dateTo: "",
  location: "",
  interviewFormatId: "",
  participantAppUserId: "",
  hrOwnerId: "",
};

const FILTER_UUID =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const FILTER_DATE = /^\\d{4}-\\d{2}-\\d{2}$/;
const FILTER_STATUSES = new Set<InterviewScheduleStatus>([
  "AVAILABLE",
  "SCHEDULED",
  "AWAITING",
  "CONFIRMED",
  "CANCELLED",
]);

function normalizedUuid(value: unknown): string {
  return typeof value === "string" && FILTER_UUID.test(value) ? value : "";
}

function normalizedDate(value: unknown): string {
  return typeof value === "string" && FILTER_DATE.test(value) ? value : "";
}

export function normalizeInterviewFilters(
  value: Partial<InterviewPageFilters> | undefined,
): InterviewPageFilters {
  const activity =
    value?.activity === "INACTIVE" || value?.activity === "ALL"
      ? value.activity
      : "ACTIVE";
  const scheduleStatus =
    typeof value?.scheduleStatus === "string" &&
    FILTER_STATUSES.has(value.scheduleStatus as InterviewScheduleStatus)
      ? (value.scheduleStatus as InterviewScheduleStatus)
      : "";
  const rawLocation = typeof value?.location === "string" ? value.location : "";
  const location =
    rawLocation === "ONLINE" ||
    (rawLocation.startsWith("ROOM:") && FILTER_UUID.test(rawLocation.slice(5)))
      ? rawLocation
      : "";
  return {
    query:
      typeof value?.query === "string" ? value.query.trim().slice(0, 256) : "",
    activity,
    unitId: normalizedUuid(value?.unitId),
    departmentTeamId: normalizedUuid(value?.departmentTeamId),
    positionId: normalizedUuid(value?.positionId),
    scheduleStatus,
    dateFrom: normalizedDate(value?.dateFrom),
    dateTo: normalizedDate(value?.dateTo),
    location,
    interviewFormatId: normalizedUuid(value?.interviewFormatId),
    participantAppUserId: normalizedUuid(value?.participantAppUserId),
    hrOwnerId: normalizedUuid(value?.hrOwnerId),
  };
}
'''
)

# ---- server: filter top-level Applications using PostgREST inner embeds; keep RLS and Application pagination ----
path = "web/src/lib/interview/server.ts"
replace_once(
    path,
    '''  type InterviewFormatOption,
  type InterviewPageData,
  type InterviewPageFilters,
  type InterviewParticipant,
''',
    '''  type InterviewFilterPositionOption,
  type InterviewFilterTeamOption,
  type InterviewFilterUnitOption,
  type InterviewFormatOption,
  type InterviewPageData,
  type InterviewPageFilters,
  type InterviewParticipant,
'''
)
replace_once(
    path,
    '''async function matchingSubmissionIds(
  client: SupabaseClient,
  rawQuery: string,
): Promise<string[] | null> {
''',
    '''function vietnamDateBoundaryIso(value: string, addDays = 0): string | null {
  const match = /^(\\d{4})-(\\d{2})-(\\d{2})$/.exec(value);
  if (!match) return null;
  const [, year, month, day] = match;
  return new Date(
    Date.UTC(
      Number(year),
      Number(month) - 1,
      Number(day) + addDays,
      -7,
      0,
      0,
    ),
  ).toISOString();
}

function hasInterviewFilters(filters: InterviewPageFilters): boolean {
  return Boolean(
    filters.scheduleStatus ||
      filters.dateFrom ||
      filters.dateTo ||
      filters.location ||
      filters.interviewFormatId ||
      filters.participantAppUserId,
  );
}

async function matchingSubmissionIds(
  client: SupabaseClient,
  rawQuery: string,
): Promise<string[] | null> {
'''
)
old_query = '''  let applicationQuery = client
    .from("applications")
    .select(
      "application_id,submission_id,unit_id,department_team_id,position_id,hr_owner_id,is_active,version_no,updated_at",
      { count: "exact" },
    )
    .order("updated_at", { ascending: false })
    .range((page - 1) * pageSize, page * pageSize - 1);
  if (filters.activity === "ACTIVE")
    applicationQuery = applicationQuery.eq("is_active", true);
  if (filters.activity === "INACTIVE")
    applicationQuery = applicationQuery.eq("is_active", false);
  if (matchedSubmissionIds)
    applicationQuery = applicationQuery.in(
      "submission_id",
      matchedSubmissionIds,
    );
'''
new_query = '''  const interviewFiltersActive = hasInterviewFilters(filters);
  const participantEmbed = filters.participantAppUserId
    ? ",filtered_participants:interview_participants!inner(app_user_id,is_current)"
    : "";
  const applicationSelect = interviewFiltersActive
    ? `application_id,submission_id,unit_id,department_team_id,position_id,hr_owner_id,is_active,version_no,updated_at,filtered_interviews:interviews!inner(interview_id,schedule_status_code,start_at,room_id,meeting_link,interview_format_id${participantEmbed})`
    : "application_id,submission_id,unit_id,department_team_id,position_id,hr_owner_id,is_active,version_no,updated_at";
  let applicationQuery = client
    .from("applications")
    .select(applicationSelect, { count: "exact" })
    .order("updated_at", { ascending: false })
    .range((page - 1) * pageSize, page * pageSize - 1);
  if (filters.activity === "ACTIVE")
    applicationQuery = applicationQuery.eq("is_active", true);
  if (filters.activity === "INACTIVE")
    applicationQuery = applicationQuery.eq("is_active", false);
  if (matchedSubmissionIds)
    applicationQuery = applicationQuery.in(
      "submission_id",
      matchedSubmissionIds,
    );
  if (filters.unitId) applicationQuery = applicationQuery.eq("unit_id", filters.unitId);
  if (filters.departmentTeamId)
    applicationQuery = applicationQuery.eq("department_team_id", filters.departmentTeamId);
  if (filters.positionId)
    applicationQuery = applicationQuery.eq("position_id", filters.positionId);
  if (filters.hrOwnerId)
    applicationQuery = applicationQuery.eq("hr_owner_id", filters.hrOwnerId);
  if (filters.scheduleStatus)
    applicationQuery = applicationQuery.eq(
      "filtered_interviews.schedule_status_code",
      filters.scheduleStatus,
    );
  const dateFrom = filters.dateFrom
    ? vietnamDateBoundaryIso(filters.dateFrom)
    : null;
  const dateToExclusive = filters.dateTo
    ? vietnamDateBoundaryIso(filters.dateTo, 1)
    : null;
  if (dateFrom)
    applicationQuery = applicationQuery.gte("filtered_interviews.start_at", dateFrom);
  if (dateToExclusive)
    applicationQuery = applicationQuery.lt(
      "filtered_interviews.start_at",
      dateToExclusive,
    );
  if (filters.interviewFormatId)
    applicationQuery = applicationQuery.eq(
      "filtered_interviews.interview_format_id",
      filters.interviewFormatId,
    );
  if (filters.location === "ONLINE")
    applicationQuery = applicationQuery.not(
      "filtered_interviews.meeting_link",
      "is",
      null,
    );
  if (filters.location.startsWith("ROOM:"))
    applicationQuery = applicationQuery.eq(
      "filtered_interviews.room_id",
      filters.location.slice(5),
    );
  if (filters.participantAppUserId) {
    applicationQuery = applicationQuery
      .eq(
        "filtered_interviews.filtered_participants.app_user_id",
        filters.participantAppUserId,
      )
      .eq("filtered_interviews.filtered_participants.is_current", true);
  }
'''
replace_once(path, old_query, new_query)

replace_once(
    path,
    '''  const [
    submissionsResult,
    unitsResult,
    teamsResult,
    positionsResult,
    ownersResult,
    interviewsResult,
    reference,
  ] = await Promise.all([
''',
    '''  const [submissionsResult, interviewsResult, reference] = await Promise.all([
'''
)
replace_once(
    path,
    '''    client.from("organizational_units").select("unit_id,name_vi"),
    client.from("department_teams").select("department_team_id,name_vi"),
    client.from("positions").select("position_id,name_vi"),
    client
      .from("app_users")
      .select("app_user_id,full_name,email,job_title,is_active"),
''',
    ''''''
)
replace_once(
    path,
    '''  const requiredResults = [
    submissionsResult,
    unitsResult,
    teamsResult,
    positionsResult,
    ownersResult,
    interviewsResult,
  ];
''',
    '''  const requiredResults = [submissionsResult, interviewsResult];
'''
)
replace_once(
    path,
    '''  const units = mapBy(unitsResult.data, "unit_id", "name_vi");
  const teams = mapBy(teamsResult.data, "department_team_id", "name_vi");
  const positions = mapBy(positionsResult.data, "position_id", "name_vi");
  const owners = mapBy(ownersResult.data, "app_user_id", "full_name");
''',
    '''  const units = new Map(reference.filterUnits.map((item) => [item.id, item.name]));
  const teams = new Map(reference.filterTeams.map((item) => [item.id, item.name]));
  const positions = new Map(
    reference.filterPositions.map((item) => [item.id, item.name]),
  );
  const owners = new Map(
    reference.filterHrOwners.map((item) => [item.id, item.name]),
  );
'''
)
# mapBy is now unused.
replace_once(
    path,
    '''  const mapBy = (rows: unknown, key: string, label: string) => {
    const map = new Map<string, string>();
    for (const row of Array.isArray(rows) ? rows : []) {
      const record = row as Record<string, unknown>;
      const id = stringValue(record[key]);
      const name = stringValue(record[label]);
      if (id && name) map.set(id, name);
    }
    return map;
  };
''',
    ''''''
)
replace_once(
    path,
    '''async function loadReferenceOptions(client: SupabaseClient): Promise<{
  formats: InterviewFormatOption[];
  rooms: InterviewRoomOption[];
  participantUsers: InterviewUserOption[];
}> {
  const [formats, rooms, users] = await Promise.all([
''',
    '''async function loadReferenceOptions(client: SupabaseClient): Promise<{
  formats: InterviewFormatOption[];
  rooms: InterviewRoomOption[];
  participantUsers: InterviewUserOption[];
  filterUnits: InterviewFilterUnitOption[];
  filterTeams: InterviewFilterTeamOption[];
  filterPositions: InterviewFilterPositionOption[];
  filterHrOwners: InterviewUserOption[];
}> {
  const [formats, rooms, users, units, teams, positions] = await Promise.all([
'''
)
replace_once(
    path,
    '''    client
      .from("app_users")
      .select("app_user_id,full_name,email,job_title,is_active")
      .eq("is_active", true)
      .order("full_name"),
  ]);
  if (formats.error || rooms.error || users.error)
''',
    '''    client
      .from("app_users")
      .select("app_user_id,full_name,email,job_title,is_active")
      .order("full_name"),
    client.from("organizational_units").select("unit_id,name_vi").order("name_vi"),
    client
      .from("department_teams")
      .select("department_team_id,unit_id,name_vi")
      .order("name_vi"),
    client
      .from("positions")
      .select("position_id,unit_id,department_team_id,name_vi")
      .order("name_vi"),
  ]);
  if (
    formats.error ||
    rooms.error ||
    users.error ||
    units.error ||
    teams.error ||
    positions.error
  )
'''
)
replace_once(
    path,
    '''    participantUsers: (Array.isArray(users.data) ? users.data : []).flatMap(
      (raw) => {
        const row = raw as Record<string, unknown>;
        const id = stringValue(row.app_user_id);
        const name = stringValue(row.full_name);
        const email = stringValue(row.email);
        if (!id || !name || !email) return [];
        return [{ id, name, email, jobTitle: stringValue(row.job_title) }];
      },
    ),
  };
}
''',
    '''    participantUsers: (Array.isArray(users.data) ? users.data : []).flatMap(
      (raw) => {
        const row = raw as Record<string, unknown>;
        const id = stringValue(row.app_user_id);
        const name = stringValue(row.full_name);
        const email = stringValue(row.email);
        if (!id || !name || !email || row.is_active !== true) return [];
        return [{ id, name, email, jobTitle: stringValue(row.job_title) }];
      },
    ),
    filterUnits: (Array.isArray(units.data) ? units.data : []).flatMap((raw) => {
      const row = raw as Record<string, unknown>;
      const id = stringValue(row.unit_id);
      const name = stringValue(row.name_vi);
      return id && name ? [{ id, name }] : [];
    }),
    filterTeams: (Array.isArray(teams.data) ? teams.data : []).flatMap((raw) => {
      const row = raw as Record<string, unknown>;
      const id = stringValue(row.department_team_id);
      const unitId = stringValue(row.unit_id);
      const name = stringValue(row.name_vi);
      return id && unitId && name ? [{ id, unitId, name }] : [];
    }),
    filterPositions: (Array.isArray(positions.data) ? positions.data : []).flatMap(
      (raw) => {
        const row = raw as Record<string, unknown>;
        const id = stringValue(row.position_id);
        const unitId = stringValue(row.unit_id);
        const name = stringValue(row.name_vi);
        return id && unitId && name
          ? [
              {
                id,
                unitId,
                departmentTeamId: stringValue(row.department_team_id),
                name,
              },
            ]
          : [];
      },
    ),
    filterHrOwners: (Array.isArray(users.data) ? users.data : []).flatMap((raw) => {
      const row = raw as Record<string, unknown>;
      const id = stringValue(row.app_user_id);
      const name = stringValue(row.full_name);
      const email = stringValue(row.email);
      return id && name && email
        ? [{ id, name, email, jobTitle: stringValue(row.job_title) }]
        : [];
    }),
  };
}
'''
)

# ---- page: render all canonical filters; keep PII query out of URL ----
path = "web/src/components/interview/InterviewPage.tsx"
replace_once(
    path,
    '''  const applyFilters = async (next: InterviewPageFilters) => {
    setFilters(next);
    setBusy(true);
''',
    '''  const applyFilters = async (next: InterviewPageFilters) => {
    if (next.dateFrom && next.dateTo && next.dateFrom > next.dateTo) {
      setFeedback({
        kind: "warning",
        message: "Từ ngày không được sau Đến ngày.",
      });
      return;
    }
    setFilters(next);
    setBusy(true);
'''
)
old_filters = '''      <fieldset className="interview-filters">
        <legend className="sr-only">Bộ lọc Interview</legend>
        <label>
          Tìm Tên / Email / SĐT
          <input
            value={filters.query}
            onChange={(event) =>
              setFilters((current) => ({
                ...current,
                query: event.target.value,
              }))
            }
            onKeyDown={(event) => {
              if (event.key === "Enter") void applyFilters(filters);
            }}
            autoComplete="off"
          />
        </label>
        <label>
          Hiển thị
          <select
            value={filters.activity}
            onChange={(event) => {
              const activity = event.target
                .value as InterviewPageFilters["activity"];
              const next = { ...filters, activity };
              void applyFilters(next);
            }}
          >
            <option value="ACTIVE">Active</option>
            <option value="INACTIVE">Inactive</option>
            <option value="ALL">All</option>
          </select>
        </label>
        <Button pending={busy} onClick={() => void applyFilters(filters)}>
          Tìm
        </Button>
        <Button
          variant="ghost"
          disabled={busy}
          onClick={() => {
            setFilters(INITIAL_INTERVIEW_FILTERS);
            void applyFilters(INITIAL_INTERVIEW_FILTERS);
          }}
        >
          Xóa lọc
        </Button>
      </fieldset>
'''
new_filters = '''      <fieldset className="interview-filters">
        <legend className="sr-only">Bộ lọc Interview</legend>
        <label>
          Tìm Tên / Email / SĐT
          <input
            value={filters.query}
            onChange={(event) =>
              setFilters((current) => ({
                ...current,
                query: event.target.value,
              }))
            }
            onKeyDown={(event) => {
              if (event.key === "Enter") void applyFilters(filters);
            }}
            autoComplete="off"
          />
        </label>
        <label>
          Hiển thị
          <select
            value={filters.activity}
            onChange={(event) =>
              setFilters((current) => ({
                ...current,
                activity: event.target.value as InterviewPageFilters["activity"],
              }))
            }
          >
            <option value="ACTIVE">Active</option>
            <option value="INACTIVE">Inactive</option>
            <option value="ALL">All</option>
          </select>
        </label>
        <label>
          Khoa / Phòng
          <select
            value={filters.unitId}
            onChange={(event) =>
              setFilters((current) => ({
                ...current,
                unitId: event.target.value,
                departmentTeamId: "",
                positionId: "",
              }))
            }
          >
            <option value="">Tất cả</option>
            {data.filterUnits.map((option) => (
              <option key={option.id} value={option.id}>
                {option.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          Ngành / Tổ
          <select
            value={filters.departmentTeamId}
            onChange={(event) =>
              setFilters((current) => ({
                ...current,
                departmentTeamId: event.target.value,
                positionId: "",
              }))
            }
          >
            <option value="">Tất cả</option>
            {data.filterTeams
              .filter((option) => !filters.unitId || option.unitId === filters.unitId)
              .map((option) => (
                <option key={option.id} value={option.id}>
                  {option.name}
                </option>
              ))}
          </select>
        </label>
        <label>
          Vị trí
          <select
            value={filters.positionId}
            onChange={(event) =>
              setFilters((current) => ({ ...current, positionId: event.target.value }))
            }
          >
            <option value="">Tất cả</option>
            {data.filterPositions
              .filter(
                (option) =>
                  (!filters.unitId || option.unitId === filters.unitId) &&
                  (!filters.departmentTeamId ||
                    option.departmentTeamId === filters.departmentTeamId),
              )
              .map((option) => (
                <option key={option.id} value={option.id}>
                  {option.name}
                </option>
              ))}
          </select>
        </label>
        <label>
          Schedule Status
          <select
            value={filters.scheduleStatus}
            onChange={(event) =>
              setFilters((current) => ({
                ...current,
                scheduleStatus: event.target.value as InterviewPageFilters["scheduleStatus"],
              }))
            }
          >
            <option value="">Tất cả</option>
            {STATUS_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
        <label>
          Từ ngày
          <input
            type="date"
            value={filters.dateFrom}
            onChange={(event) =>
              setFilters((current) => ({ ...current, dateFrom: event.target.value }))
            }
          />
        </label>
        <label>
          Đến ngày
          <input
            type="date"
            min={filters.dateFrom || undefined}
            value={filters.dateTo}
            onChange={(event) =>
              setFilters((current) => ({ ...current, dateTo: event.target.value }))
            }
          />
        </label>
        <label>
          Địa điểm
          <select
            value={filters.location}
            onChange={(event) =>
              setFilters((current) => ({ ...current, location: event.target.value }))
            }
          >
            <option value="">Tất cả</option>
            <option value="ONLINE">Online / Meeting Link</option>
            {data.rooms.map((room) => (
              <option key={room.id} value={`ROOM:${room.id}`}>
                {room.name}{room.building ? ` — ${room.building}` : ""}
              </option>
            ))}
          </select>
        </label>
        <label>
          Hình thức
          <select
            value={filters.interviewFormatId}
            onChange={(event) =>
              setFilters((current) => ({
                ...current,
                interviewFormatId: event.target.value,
              }))
            }
          >
            <option value="">Tất cả</option>
            {data.formats.map((format) => (
              <option key={format.id} value={format.id}>
                {format.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          Participant
          <select
            value={filters.participantAppUserId}
            onChange={(event) =>
              setFilters((current) => ({
                ...current,
                participantAppUserId: event.target.value,
              }))
            }
          >
            <option value="">Tất cả</option>
            {data.participantUsers.map((user) => (
              <option key={user.id} value={user.id}>
                {user.name} — {user.email}
              </option>
            ))}
          </select>
        </label>
        <label>
          HR phụ trách
          <select
            value={filters.hrOwnerId}
            onChange={(event) =>
              setFilters((current) => ({ ...current, hrOwnerId: event.target.value }))
            }
          >
            <option value="">Tất cả</option>
            {data.filterHrOwners.map((user) => (
              <option key={user.id} value={user.id}>
                {user.name} — {user.email}
              </option>
            ))}
          </select>
        </label>
        <Button pending={busy} onClick={() => void applyFilters(filters)}>
          Áp dụng
        </Button>
        <Button
          variant="ghost"
          disabled={busy}
          onClick={() => {
            const reset = { ...INITIAL_INTERVIEW_FILTERS, activity: initialActivity };
            setFilters(reset);
            void applyFilters(reset);
          }}
        >
          Xóa lọc
        </Button>
      </fieldset>
'''
replace_once(path, old_filters, new_filters)

# ---- focused model tests: filter normalization stays bounded and untrusted IDs do not reach Supabase ----
path = "web/src/__tests__/interview-model.test.ts"
replace_once(
    path,
    '''  assert.deepEqual(normalizeInterviewFilters({ activity: "ACTIVE" }), {
    query: "",
    activity: "ACTIVE",
  });
});
''',
    '''  assert.deepEqual(normalizeInterviewFilters({ activity: "ACTIVE" }), {
    query: "",
    activity: "ACTIVE",
    unitId: "",
    departmentTeamId: "",
    positionId: "",
    scheduleStatus: "",
    dateFrom: "",
    dateTo: "",
    location: "",
    interviewFormatId: "",
    participantAppUserId: "",
    hrOwnerId: "",
  });
});

test("Interview canonical filters normalize UUIDs, status, dates and location safely", () => {
  const uuid = "11111111-1111-4111-8111-111111111111";
  const normalized = normalizeInterviewFilters({
    unitId: uuid,
    departmentTeamId: "not-a-uuid",
    positionId: uuid,
    scheduleStatus: "CONFIRMED",
    dateFrom: "2026-09-08",
    dateTo: "bad-date",
    location: `ROOM:${uuid}`,
    interviewFormatId: uuid,
    participantAppUserId: uuid,
    hrOwnerId: uuid,
  });
  assert.equal(normalized.unitId, uuid);
  assert.equal(normalized.departmentTeamId, "");
  assert.equal(normalized.positionId, uuid);
  assert.equal(normalized.scheduleStatus, "CONFIRMED");
  assert.equal(normalized.dateFrom, "2026-09-08");
  assert.equal(normalized.dateTo, "");
  assert.equal(normalized.location, `ROOM:${uuid}`);
  assert.equal(normalized.interviewFormatId, uuid);
  assert.equal(normalized.participantAppUserId, uuid);
  assert.equal(normalized.hrOwnerId, uuid);
  assert.equal(
    normalizeInterviewFilters({ scheduleStatus: "INVALID" as never }).scheduleStatus,
    "",
  );
  assert.equal(normalizeInterviewFilters({ location: "javascript:bad" }).location, "");
});
'''
)

print("canonical S04 Interview filters applied")
