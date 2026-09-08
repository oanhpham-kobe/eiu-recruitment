"use client";

import { useCallback, useMemo, useRef, useState } from "react";
import {
  addInterviewParticipantAction,
  changeInterviewStatusAction,
  copyInterviewScheduleAction,
  createInterviewApplicationAction,
  createNextRoundAction,
  deleteOrInactivateApplicationAction,
  deleteOrInactivateInterviewAction,
  getInterviewAssignmentOptionsAction,
  queryInterviewPageAction,
  reactivateApplicationAction,
  reactivateInterviewAction,
  readdInterviewParticipantAction,
  removeInterviewParticipantAction,
  reorderInterviewParticipantsAction,
  rescheduleConfirmedAction,
  saveInterviewScheduleAction,
  searchApplicationOptionsAction,
  searchSubmissionOptionsAction,
} from "@/app/interviews/actions";
import { AsyncStatus } from "@/components/ui/AsyncStatus";
import { Button } from "@/components/ui/Button";
import { Dialog } from "@/components/ui/Dialog";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { StatusMenu } from "@/components/ui/StatusMenu";
import { TableScrollContainer } from "@/components/ui/TableScrollContainer";
import type { AssignmentOptions } from "@/lib/application-inbox/submission-detail-model";
import {
  type ApplicationSelectorOption,
  formatInterviewTime,
  INITIAL_INTERVIEW_FILTERS,
  INTERVIEW_COLUMNS,
  INTERVIEW_STATUS_LABEL,
  type InterviewApplicationGroup,
  type InterviewPageData,
  type InterviewPageFilters,
  type InterviewRound,
  type InterviewScheduleStatus,
  nextExpandedApplicationId,
  type SubmissionSelectorOption,
} from "@/lib/interview/model";
import {
  ApplicationAssignmentDialog,
  CopyScheduleDialog,
} from "./InterviewDialogs";
import { InterviewDrawer } from "./InterviewDrawer";

const STATUS_OPTIONS = Object.entries(INTERVIEW_STATUS_LABEL).map(
  ([value, label]) => ({ value, label }),
);

type Feedback = {
  kind: "success" | "error" | "warning";
  message: string;
} | null;
type MutationResult =
  | { success: true; data: unknown }
  | { success: false; error: { code?: string; message: string } };

function statusTone(
  status: InterviewScheduleStatus,
): "success" | "warning" | "danger" | "info" | "neutral" {
  if (status === "CONFIRMED") return "success";
  if (status === "AWAITING") return "warning";
  if (status === "AVAILABLE") return "danger";
  if (status === "SCHEDULED") return "info";
  return "neutral";
}

function latestRound(group: InterviewApplicationGroup): InterviewRound | null {
  return [...group.rounds].sort((a, b) => b.roundNo - a.roundNo)[0] ?? null;
}

export function InterviewPage({
  initialData,
  initialActivity = "ACTIVE",
}: {
  initialData: InterviewPageData;
  initialActivity?: InterviewPageFilters["activity"];
}) {
  const [data, setData] = useState(initialData);
  const [filters, setFilters] = useState<InterviewPageFilters>({
    ...INITIAL_INTERVIEW_FILTERS,
    activity: initialActivity,
  });
  const [expandedApplicationId, setExpandedApplicationId] = useState<
    string | null
  >(null);
  const [selectedInterviewId, setSelectedInterviewId] = useState<string | null>(
    null,
  );
  const [drawerInterviewId, setDrawerInterviewId] = useState<string | null>(
    null,
  );
  const [applicationDialogOpen, setApplicationDialogOpen] = useState(false);
  const [copySourceId, setCopySourceId] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [feedback, setFeedback] = useState<Feedback>(null);
  const [confirmState, setConfirmState] = useState<null | {
    title: string;
    message: string;
    execute: () => Promise<void>;
  }>(null);
  const intentKeys = useRef(new Map<string, string>());

  const groupsByInterview = useMemo(() => {
    const map = new Map<
      string,
      { application: InterviewApplicationGroup; round: InterviewRound }
    >();
    for (const application of data.groups)
      for (const round of application.rounds)
        map.set(round.interviewId, { application, round });
    return map;
  }, [data.groups]);
  const selected = selectedInterviewId
    ? (groupsByInterview.get(selectedInterviewId) ?? null)
    : null;
  const drawer = drawerInterviewId
    ? (groupsByInterview.get(drawerInterviewId) ?? null)
    : null;
  const copySource = copySourceId
    ? (groupsByInterview.get(copySourceId) ?? null)
    : null;

  const intentSignature = (operation: string, payload: unknown) =>
    `${operation}:${JSON.stringify(payload)}`;
  const keyFor = (operation: string, payload: unknown) => {
    const signature = intentSignature(operation, payload);
    const existing = intentKeys.current.get(signature);
    if (existing) return { signature, key: existing };
    const key = crypto.randomUUID();
    intentKeys.current.set(signature, key);
    return { signature, key };
  };

  const refresh = useCallback(
    async (page = data.page, nextFilters = filters) => {
      const next = await queryInterviewPageAction({
        filters: nextFilters,
        page,
      });
      setData(next);
      setSelectedInterviewId((id) =>
        id &&
        next.groups.some((group) =>
          group.rounds.some((round) => round.interviewId === id),
        )
          ? id
          : null,
      );
      setDrawerInterviewId((id) =>
        id &&
        next.groups.some((group) =>
          group.rounds.some((round) => round.interviewId === id),
        )
          ? id
          : null,
      );
      return next;
    },
    [data.page, filters],
  );

  const runMutation = useCallback(
    async (
      execute: () => Promise<MutationResult>,
      successMessage: string,
      idempotencySignature?: string,
    ) => {
      setBusy(true);
      setFeedback(null);
      try {
        const result = await execute();
        if (!result.success) {
          setFeedback({
            kind: result.error.code === "STALE_VERSION" ? "warning" : "error",
            message: result.error.message,
          });
          if (result.error.code === "STALE_VERSION") await refresh();
          return false;
        }
        if (idempotencySignature)
          intentKeys.current.delete(idempotencySignature);
        await refresh();
        setFeedback({ kind: "success", message: successMessage });
        return true;
      } catch {
        setFeedback({
          kind: "error",
          message: "Không thể hoàn tất thao tác. Vui lòng thử lại.",
        });
        return false;
      } finally {
        setBusy(false);
      }
    },
    [refresh],
  );

  const applyFilters = async (next: InterviewPageFilters) => {
    setFilters(next);
    setBusy(true);
    try {
      const nextData = await queryInterviewPageAction({
        filters: next,
        page: 1,
      });
      setData(nextData);
      setExpandedApplicationId(null);
      setSelectedInterviewId(null);
    } catch {
      setFeedback({
        kind: "error",
        message: "Không thể tải bộ lọc Interview.",
      });
    } finally {
      setBusy(false);
    }
  };

  const changeStatus = async (
    round: InterviewRound,
    status: InterviewScheduleStatus,
  ) => {
    await runMutation(
      () =>
        changeInterviewStatusAction({
          interviewId: round.interviewId,
          status,
          expectedVersion: round.versionNo,
        }),
      `Đã đổi trạng thái sang ${INTERVIEW_STATUS_LABEL[status]}.`,
    );
  };

  const createNextRound = async (application: InterviewApplicationGroup) => {
    const payload = { applicationId: application.applicationId };
    const intent = keyFor("create-next-round", payload);
    await runMutation(
      () => createNextRoundAction({ ...payload, idempotencyKey: intent.key }),
      "Đã tạo vòng phỏng vấn tiếp theo. Demo Topic để trống theo quy tắc.",
      intent.signature,
    );
  };

  const requestCreateNextRound = (application: InterviewApplicationGroup) => {
    setConfirmState({
      title: "Tạo vòng phỏng vấn tiếp theo",
      message:
        "Server sẽ kiểm tra vòng mới nhất còn Active và chưa HIRED. Demo Topic của vòng mới luôn để trống.",
      execute: async () => {
        await createNextRound(application);
      },
    });
  };

  const searchSubmissions = useCallback(
    async (query: string): Promise<SubmissionSelectorOption[]> => {
      const result = await searchSubmissionOptionsAction(query);
      if (!result.success) {
        setFeedback({ kind: "error", message: result.error });
        return [];
      }
      return result.data;
    },
    [],
  );
  const loadAssignment =
    useCallback(async (): Promise<AssignmentOptions | null> => {
      const result = await getInterviewAssignmentOptionsAction();
      if (!result.success) {
        setFeedback({ kind: "error", message: result.error });
        return null;
      }
      return result.data;
    }, []);
  const searchApplications = useCallback(
    async (query: string): Promise<ApplicationSelectorOption[]> => {
      const result = await searchApplicationOptionsAction(query);
      if (!result.success) {
        setFeedback({ kind: "error", message: result.error });
        return [];
      }
      return result.data;
    },
    [],
  );

  const renderStatus = (round: InterviewRound) =>
    data.permissions.canChangeStatus ? (
      <div
        className={`interview-status-menu interview-status-menu--${round.scheduleStatus.toLowerCase()}`}
      >
        <StatusMenu
          label={INTERVIEW_STATUS_LABEL[round.scheduleStatus]}
          currentValue={round.scheduleStatus}
          options={STATUS_OPTIONS}
          onSelect={(status) =>
            void changeStatus(round, status as InterviewScheduleStatus)
          }
        />
      </div>
    ) : (
      <StatusBadge tone={statusTone(round.scheduleStatus)} operationalInterview>
        {INTERVIEW_STATUS_LABEL[round.scheduleStatus]}
      </StatusBadge>
    );

  const locationText = (round: InterviewRound) => {
    if (round.roomId)
      return (
        data.rooms.find((room) => room.id === round.roomId)?.name ?? "Phòng"
      );
    if (round.meetingLink) return "Online / Meeting Link";
    return "—";
  };

  const openDeleteInterview = (round: InterviewRound) => {
    setConfirmState({
      title: `Xóa / Ngừng hoạt động Vòng ${round.roundNo}`,
      message:
        "Chỉ vòng mới nhất hợp lệ mới được xử lý. Server sẽ quyết định hard delete hay inactivate theo lịch sử sử dụng.",
      execute: async () => {
        const ok = await runMutation(
          () =>
            deleteOrInactivateInterviewAction({
              interviewId: round.interviewId,
              expectedVersion: round.versionNo,
            }),
          "Đã xử lý vòng phỏng vấn.",
        );
        if (ok) {
          setDrawerInterviewId(null);
          setSelectedInterviewId(null);
        }
      },
    });
  };

  return (
    <section className="interview-page" aria-labelledby="interview-page-title">
      <div className="interview-page-heading">
        <div>
          <h1 id="interview-page-title">Lịch phỏng vấn / Interviews</h1>
          <p>
            Quản lý Application, vòng phỏng vấn, logistics và người tham dự.
          </p>
        </div>
      </div>

      <fieldset className="interview-toolbar">
        <legend className="sr-only">Thao tác Interview</legend>
        {data.permissions.canCreateApplication ? (
          <Button
            variant="primary"
            onClick={() => setApplicationDialogOpen(true)}
          >
            Ứng tuyển
          </Button>
        ) : null}
        <Button
          disabled={!selected || busy}
          onClick={() =>
            selected && setDrawerInterviewId(selected.round.interviewId)
          }
        >
          Tạo lịch / Chi tiết
        </Button>
        {data.permissions.canManage && selected ? (
          <Button
            disabled={busy || !selected.application.isActive}
            onClick={() => requestCreateNextRound(selected.application)}
          >
            Tạo vòng tiếp theo
          </Button>
        ) : null}
        {data.permissions.canManage && selected ? (
          <Button
            variant="danger"
            disabled={busy}
            onClick={() => openDeleteInterview(selected.round)}
          >
            Xóa
          </Button>
        ) : null}
        {data.permissions.canChangeStatus && selected ? (
          <StatusMenu
            label={`Đổi status: ${INTERVIEW_STATUS_LABEL[selected.round.scheduleStatus]}`}
            currentValue={selected.round.scheduleStatus}
            options={STATUS_OPTIONS}
            onSelect={(status) =>
              void changeStatus(
                selected.round,
                status as InterviewScheduleStatus,
              )
            }
          />
        ) : null}
      </fieldset>

      <fieldset className="interview-filters">
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

      {feedback ? (
        <AsyncStatus kind={feedback.kind}>{feedback.message}</AsyncStatus>
      ) : null}

      <TableScrollContainer className="interview-table-scroll">
        <table className="interview-table">
          <colgroup>
            {INTERVIEW_COLUMNS.map((width) => (
              <col key={width} style={{ width }} />
            ))}
          </colgroup>
          <thead>
            <tr>
              <th scope="col">Chọn</th>
              <th scope="col">Ứng viên / Application</th>
              <th scope="col">Thời gian</th>
              <th scope="col">Địa điểm</th>
              <th scope="col">Trạng thái</th>
              <th scope="col">Ghi chú</th>
              <th scope="col">Action</th>
            </tr>
          </thead>
          <tbody>
            {data.groups.map((application) => {
              const latest = latestRound(application);
              const expanded =
                expandedApplicationId === application.applicationId;
              return (
                <ApplicationRows
                  key={application.applicationId}
                  application={application}
                  latest={latest}
                  expanded={expanded}
                  selectedInterviewId={selectedInterviewId}
                  busy={busy}
                  canManage={data.permissions.canManage}
                  canReactivateApplication={
                    data.permissions.canReactivateApplication
                  }
                  canDeleteApplication={data.permissions.canDeleteApplication}
                  renderStatus={renderStatus}
                  locationText={locationText}
                  onToggle={() =>
                    setExpandedApplicationId((current) =>
                      nextExpandedApplicationId(
                        current,
                        application.applicationId,
                      ),
                    )
                  }
                  onSelect={setSelectedInterviewId}
                  onOpen={setDrawerInterviewId}
                  onCopy={setCopySourceId}
                  onCreateNext={() => requestCreateNextRound(application)}
                  onReactivateApplication={() => {
                    setConfirmState({
                      title: "Kích hoạt lại Application",
                      message:
                        "Server sẽ revalidate HR phụ trách, current Participants và mọi resource conflict còn liên quan trước khi kích hoạt.",
                      execute: async () => {
                        await runMutation(
                          () =>
                            reactivateApplicationAction({
                              applicationId: application.applicationId,
                              expectedVersion: application.versionNo,
                            }),
                          "Đã kích hoạt lại Application.",
                        );
                      },
                    });
                  }}
                  onDeleteApplication={() => {
                    setConfirmState({
                      title: "Xóa / Ngừng hoạt động Application",
                      message:
                        "Server quyết định hard delete hoặc inactivate; lịch sử Interview không bị client tự xóa dây chuyền.",
                      execute: async () => {
                        await runMutation(
                          () =>
                            deleteOrInactivateApplicationAction(
                              application.applicationId,
                            ),
                          "Đã xử lý Application.",
                        );
                      },
                    });
                  }}
                />
              );
            })}
            {!data.groups.length ? (
              <tr>
                <td colSpan={7} className="interview-empty">
                  Không có Application phù hợp.
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </TableScrollContainer>

      <nav className="interview-pagination" aria-label="Phân trang Application">
        <Button
          disabled={busy || data.page <= 1}
          onClick={() => void refresh(data.page - 1)}
        >
          Trang trước
        </Button>
        <span>
          Trang {data.page} / {data.pageCount}
        </span>
        <Button
          disabled={busy || data.page >= data.pageCount}
          onClick={() => void refresh(data.page + 1)}
        >
          Trang sau
        </Button>
      </nav>

      {drawer ? (
        <InterviewDrawer
          key={`${drawer.round.interviewId}-${drawer.round.versionNo}`}
          open
          application={drawer.application}
          round={drawer.round}
          formats={data.formats}
          rooms={data.rooms}
          users={data.participantUsers}
          permissions={data.permissions}
          pending={busy}
          onClose={() => setDrawerInterviewId(null)}
          onSave={(input) => {
            const payload = {
              interviewId: drawer.round.interviewId,
              ...input,
              expectedVersion: drawer.round.versionNo,
            };
            const intent = keyFor("save-schedule", payload);
            void runMutation(
              () =>
                saveInterviewScheduleAction({
                  ...payload,
                  idempotencyKey: intent.key,
                }),
              "Đã lưu lịch từ trạng thái server trả về.",
              intent.signature,
            );
          }}
          onRescheduleConfirmed={(input) => {
            const payload = {
              interviewId: drawer.round.interviewId,
              ...input,
              expectedVersion: drawer.round.versionNo,
            };
            const intent = keyFor("reschedule-confirmed", payload);
            void runMutation(
              () =>
                rescheduleConfirmedAction({
                  ...payload,
                  idempotencyKey: intent.key,
                }),
              "Đã xếp lại lịch; trạng thái server chuyển sang Chờ xác nhận.",
              intent.signature,
            );
          }}
          onStatus={(status) => void changeStatus(drawer.round, status)}
          onAddParticipant={(appUserId) => {
            const payload = {
              interviewId: drawer.round.interviewId,
              appUserId,
            };
            const intent = keyFor("add-participant", payload);
            void runMutation(
              () =>
                addInterviewParticipantAction({
                  ...payload,
                  idempotencyKey: intent.key,
                }),
              "Đã thêm người tham dự.",
              intent.signature,
            );
          }}
          onRemoveParticipant={(participant) => {
            setConfirmState({
              title: `Gỡ ${participant.name}`,
              message: participant.hasReportHistory
                ? "Người này đã có report. Report lịch sử được giữ lại nhưng không render trong PDF hiện hành khi Participant không còn current."
                : "Người này sẽ không còn là Participant hiện tại của vòng.",
              execute: async () => {
                await runMutation(
                  () =>
                    removeInterviewParticipantAction({
                      interviewParticipantId:
                        participant.interviewParticipantId,
                      expectedVersion: participant.versionNo,
                    }),
                  "Đã gỡ người tham dự.",
                );
              },
            });
          }}
          onReaddParticipant={(participant, restoreMode) => {
            const payload = {
              interviewParticipantId: participant.interviewParticipantId,
              restoreMode,
            };
            const intent = keyFor("readd-participant", payload);
            void runMutation(
              () =>
                readdInterviewParticipantAction({
                  ...payload,
                  idempotencyKey: intent.key,
                }),
              restoreMode === "RESTORE_OLD_REPORT"
                ? "Đã thêm lại Participant và khôi phục report cũ."
                : "Đã thêm lại Participant với report mới.",
              intent.signature,
            );
          }}
          onReorderParticipants={(participants) => {
            void runMutation(
              () =>
                reorderInterviewParticipantsAction({
                  interviewId: drawer.round.interviewId,
                  participantIds: participants.map(
                    (p) => p.interviewParticipantId,
                  ),
                  expectedVersions: participants.map((p) => p.versionNo),
                }),
              "Đã cập nhật thứ tự Participant.",
            );
          }}
          onReactivateInterview={() => {
            setConfirmState({
              title: "Kích hoạt lại Interview",
              message:
                "Đây là Interview Reactivate, tách biệt với Application Reactivate. Server sẽ revalidate resource conflicts và current Participants.",
              execute: async () => {
                await runMutation(
                  () =>
                    reactivateInterviewAction({
                      interviewId: drawer.round.interviewId,
                      expectedVersion: drawer.round.versionNo,
                    }),
                  "Đã kích hoạt lại Interview.",
                );
              },
            });
          }}
          onDeleteInterview={() => openDeleteInterview(drawer.round)}
        />
      ) : null}

      <ApplicationAssignmentDialog
        open={applicationDialogOpen}
        pending={busy}
        onClose={() => setApplicationDialogOpen(false)}
        onSearchSubmissions={searchSubmissions}
        onLoadAssignmentOptions={loadAssignment}
        onSubmit={(input) => {
          const intent = keyFor("create-application", input);
          void runMutation(
            async () => {
              const result = await createInterviewApplicationAction({
                ...input,
                idempotencyKey: intent.key,
              });
              return result.success
                ? { success: true as const, data: result.data }
                : {
                    success: false as const,
                    error: { code: result.code, message: result.error },
                  };
            },
            "Đã tạo / cập nhật Application và Vòng 1 theo contract server.",
            intent.signature,
          ).then((ok) => {
            if (ok) setApplicationDialogOpen(false);
          });
        }}
      />

      {copySource ? (
        <CopyScheduleDialog
          key={`${copySource.round.interviewId}-${copySource.round.versionNo}`}
          open
          sourceApplication={copySource.application}
          sourceRound={copySource.round}
          formats={data.formats}
          rooms={data.rooms}
          users={data.participantUsers}
          pending={busy}
          onClose={() => setCopySourceId(null)}
          onSearchApplications={searchApplications}
          onSubmit={(input) => {
            const payload = {
              sourceInterviewId: copySource.round.interviewId,
              targetApplicationId: input.target.applicationId,
              expectedSourceVersion: copySource.round.versionNo,
              expectedTargetApplicationVersion: input.target.versionNo,
              expectedTargetRoundId: input.target.latestRoundId,
              expectedTargetRoundVersion: input.target.latestRoundVersionNo,
              startAt: input.startAt,
              endAt: input.endAt,
              interviewFormatId: input.interviewFormatId,
              roomId: input.roomId,
              meetingLink: input.meetingLink,
              interviewNote: input.interviewNote,
              participantAppUserIds: input.participantAppUserIds,
            };
            const intent = keyFor("copy-schedule", payload);
            void runMutation(
              () =>
                copyInterviewScheduleAction({
                  ...payload,
                  idempotencyKey: intent.key,
                }),
              "Đã Save Copy atomically. Demo Topic của vòng đích để trống.",
              intent.signature,
            ).then((ok) => {
              if (ok) setCopySourceId(null);
            });
          }}
        />
      ) : null}

      <Dialog
        open={Boolean(confirmState)}
        title={confirmState?.title ?? "Xác nhận"}
        onClose={() => setConfirmState(null)}
        footer={
          <div className="interview-confirm-actions">
            <Button onClick={() => setConfirmState(null)}>Hủy</Button>
            <Button
              variant="danger"
              pending={busy}
              onClick={async () => {
                const execute = confirmState?.execute;
                if (!execute) return;
                await execute();
                setConfirmState(null);
              }}
            >
              Xác nhận
            </Button>
          </div>
        }
      >
        <p>{confirmState?.message}</p>
      </Dialog>
    </section>
  );
}

function ApplicationRows({
  application,
  latest,
  expanded,
  selectedInterviewId,
  busy,
  canManage,
  canReactivateApplication,
  canDeleteApplication,
  renderStatus,
  locationText,
  onToggle,
  onSelect,
  onOpen,
  onCopy,
  onCreateNext,
  onReactivateApplication,
  onDeleteApplication,
}: {
  application: InterviewApplicationGroup;
  latest: InterviewRound | null;
  expanded: boolean;
  selectedInterviewId: string | null;
  busy: boolean;
  canManage: boolean;
  canReactivateApplication: boolean;
  canDeleteApplication: boolean;
  renderStatus: (round: InterviewRound) => React.ReactNode;
  locationText: (round: InterviewRound) => string;
  onToggle: () => void;
  onSelect: (id: string | null) => void;
  onOpen: (id: string) => void;
  onCopy: (id: string) => void;
  onCreateNext: () => void;
  onReactivateApplication: () => void;
  onDeleteApplication: () => void;
}) {
  const identity = `${application.positionName} - ${application.departmentTeamName ? `${application.departmentTeamName} - ` : ""}${application.unitName}`;
  const selectId = latest?.interviewId ?? null;
  return (
    <>
      <tr
        className={`interview-application-row ${application.isActive ? "" : "is-inactive"}`}
        onClick={(event) => {
          const target = event.target as HTMLElement;
          if (target.closest("button,input,a,select,textarea")) return;
          onToggle();
        }}
      >
        <td data-label="Chọn">
          {selectId ? (
            <input
              type="checkbox"
              aria-label={`Chọn ${application.candidateName}`}
              checked={selectedInterviewId === selectId}
              onChange={(event) =>
                onSelect(event.target.checked ? selectId : null)
              }
            />
          ) : null}
        </td>
        <th scope="row" data-label="Ứng viên / Application">
          <button
            type="button"
            className="interview-expand-button"
            aria-expanded={expanded}
            onClick={(event) => {
              event.stopPropagation();
              onToggle();
            }}
          >
            <span aria-hidden="true">{expanded ? "▾" : "▸"}</span>
            <span>
              <strong>{application.candidateName}</strong>
              <small>{identity}</small>
              <small>{application.candidateEmail}</small>
              {!application.isActive ? (
                <em>Application — Không hoạt động</em>
              ) : null}
            </span>
          </button>
        </th>
        <td data-label="Thời gian">
          {latest ? formatInterviewTime(latest.startAt, latest.endAt) : "—"}
        </td>
        <td data-label="Địa điểm">{latest ? locationText(latest) : "—"}</td>
        <td data-label="Trạng thái">{latest ? renderStatus(latest) : "—"}</td>
        <td data-label="Ghi chú">{latest?.interviewNote ?? "—"}</td>
        <td data-label="Action">
          <div className="interview-row-actions">
            {latest ? (
              <Button
                variant="ghost"
                onClick={() => onOpen(latest.interviewId)}
              >
                Mở
              </Button>
            ) : null}
            {canManage && application.isActive ? (
              <Button variant="ghost" disabled={busy} onClick={onCreateNext}>
                + Vòng
              </Button>
            ) : null}
            {!application.isActive && canReactivateApplication ? (
              <Button
                variant="ghost"
                disabled={busy}
                onClick={onReactivateApplication}
              >
                Reactivate App
              </Button>
            ) : null}
            {canDeleteApplication ? (
              <Button
                variant="ghost"
                disabled={busy}
                onClick={onDeleteApplication}
              >
                Xóa App
              </Button>
            ) : null}
          </div>
        </td>
      </tr>
      {expanded
        ? application.rounds.map((round) => (
            <tr
              key={round.interviewId}
              className={`interview-round-row ${round.isActive ? "" : "is-inactive"}`}
            >
              <td data-label="Chọn">
                <input
                  type="checkbox"
                  aria-label={`Chọn Vòng ${round.roundNo}`}
                  checked={selectedInterviewId === round.interviewId}
                  onChange={(event) =>
                    onSelect(event.target.checked ? round.interviewId : null)
                  }
                />
              </td>
              <th scope="row" data-label="Ứng viên / Application">
                <strong>Vòng {round.roundNo}</strong>
                <small>
                  {round.isActive ? "Đang hoạt động" : "Không hoạt động"}
                </small>
              </th>
              <td data-label="Thời gian">
                {formatInterviewTime(round.startAt, round.endAt)}
              </td>
              <td data-label="Địa điểm">{locationText(round)}</td>
              <td data-label="Trạng thái">{renderStatus(round)}</td>
              <td data-label="Ghi chú">{round.interviewNote ?? "—"}</td>
              <td data-label="Action">
                <div className="interview-row-actions">
                  <Button
                    variant="ghost"
                    onClick={() => onOpen(round.interviewId)}
                  >
                    Chi tiết
                  </Button>
                  {canManage ? (
                    <Button
                      variant="ghost"
                      onClick={() => onCopy(round.interviewId)}
                    >
                      Copy
                    </Button>
                  ) : null}
                </div>
              </td>
            </tr>
          ))
        : null}
    </>
  );
}
