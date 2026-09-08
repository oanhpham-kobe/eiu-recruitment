from pathlib import Path

path = Path("web/src/lib/interview/server.ts")
text = path.read_text(encoding="utf-8")

old = '''async function matchingSubmissionIds(
  client: SupabaseClient,
  rawQuery: string,
): Promise<string[] | null> {
  const query = safeSearchTerm(rawQuery);
  if (!query) return null;
  const pattern = `%${query}%`;
  const { data, error } = await client
    .from("submissions")
    .select("submission_id")
    .or(
      `full_name.ilike.${pattern},email_snapshot.ilike.${pattern},phone.ilike.${pattern}`,
    )
    .limit(250);
  if (error) throw new InterviewReadError();
  return (Array.isArray(data) ? data : [])
    .map((row) =>
      stringValue((row as { submission_id?: unknown }).submission_id),
    )
    .filter((id): id is string => id !== null);
}

'''
if text.count(old) != 1:
    raise RuntimeError("matchingSubmissionIds block not found exactly once")
text = text.replace(old, "", 1)

old = '''  const matchedSubmissionIds = await matchingSubmissionIds(
    client,
    filters.query,
  );
  if (matchedSubmissionIds?.length === 0) {
    const reference = await loadReferenceOptions(client);
    return {
      groups: [],
      page: 1,
      pageCount: 1,
      permissions: actorPermissions,
      ...reference,
    };
  }

  const interviewFiltersActive = hasInterviewFilters(filters);
  const participantEmbed = filters.participantAppUserId
    ? ",filtered_participants:interview_participants!inner(app_user_id,is_current)"
    : "";
  const applicationSelect = interviewFiltersActive
    ? `application_id,submission_id,unit_id,department_team_id,position_id,hr_owner_id,is_active,version_no,updated_at,filtered_interviews:interviews!inner(interview_id,schedule_status_code,start_at,room_id,meeting_link,interview_format_id${participantEmbed})`
    : "application_id,submission_id,unit_id,department_team_id,position_id,hr_owner_id,is_active,version_no,updated_at";
'''
new = '''  const submissionSearch = safeSearchTerm(filters.query);
  const interviewFiltersActive = hasInterviewFilters(filters);
  const participantEmbed = filters.participantAppUserId
    ? ",filtered_participants:interview_participants!inner(app_user_id,is_current)"
    : "";
  const submissionEmbed = submissionSearch
    ? ",filtered_submission:submissions!inner(submission_id,full_name,email_snapshot,phone)"
    : "";
  const interviewEmbed = interviewFiltersActive
    ? `,filtered_interviews:interviews!inner(interview_id,schedule_status_code,start_at,room_id,meeting_link,interview_format_id${participantEmbed})`
    : "";
  const applicationSelect = `application_id,submission_id,unit_id,department_team_id,position_id,hr_owner_id,is_active,version_no,updated_at${submissionEmbed}${interviewEmbed}`;
'''
if text.count(old) != 1:
    raise RuntimeError("loadInterviewPage search/select block not found exactly once")
text = text.replace(old, new, 1)

old = '''  if (filters.activity === "INACTIVE")
    applicationQuery = applicationQuery.eq("is_active", false);
  if (matchedSubmissionIds)
    applicationQuery = applicationQuery.in(
      "submission_id",
      matchedSubmissionIds,
    );
  if (filters.unitId)
'''
new = '''  if (filters.activity === "INACTIVE")
    applicationQuery = applicationQuery.eq("is_active", false);
  if (submissionSearch) {
    const pattern = `%${submissionSearch}%`;
    applicationQuery = applicationQuery.or(
      `full_name.ilike.${pattern},email_snapshot.ilike.${pattern},phone.ilike.${pattern}`,
      { referencedTable: "filtered_submission" },
    );
  }
  if (filters.unitId)
'''
if text.count(old) != 1:
    raise RuntimeError("application search filter block not found exactly once")
text = text.replace(old, new, 1)

path.write_text(text, encoding="utf-8")
print("application-scoped PII search repair applied")
