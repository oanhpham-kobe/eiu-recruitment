"use client";

import {
  useCallback,
  useEffect,
  useReducer,
  useRef,
  useState,
  useTransition,
} from "react";
import { queryApplicationInbox } from "@/app/application-inbox-actions";
import {
  ApplicationInboxTableRows,
  SUBMISSION_STATUS_LABEL,
} from "@/components/inbox/ApplicationInboxTableRows";
import { SubmissionDetailDrawer } from "@/components/inbox/SubmissionDetailDrawer";
import {
  APPLICATION_INBOX_COLUMNS,
  type ApplicationInboxFilters,
  type ApplicationInboxGroup,
  INITIAL_APPLICATION_INBOX_FILTERS,
  nextExpandedCandidateId,
} from "@/lib/application-inbox/model";

export interface ApplicationInboxTableProps {
  groups: ApplicationInboxGroup[];
  errorMessage?: string;
  loading?: boolean;
  page?: number;
  pageCount?: number;
}

interface ApplicationInboxPage {
  groups: ApplicationInboxGroup[];
  page: number;
  pageCount: number;
}

export interface ApplicationInboxReadState {
  errorMessage?: string;
  inbox: ApplicationInboxPage;
}

export type ApplicationInboxReadAction =
  | { inbox: ApplicationInboxPage; type: "loaded" }
  | { message: string; type: "failed" };

export function reduceApplicationInboxReadState(
  state: ApplicationInboxReadState,
  action: ApplicationInboxReadAction,
): ApplicationInboxReadState {
  if (action.type === "loaded") {
    return { inbox: action.inbox };
  }
  return { ...state, errorMessage: action.message };
}

function hasActiveFilters(filters: ApplicationInboxFilters): boolean {
  return Object.values(filters).some(
    (value) => value !== "" && value !== "ALL",
  );
}

export function ApplicationInboxTable({
  groups,
  errorMessage,
  loading = false,
  page = 1,
  pageCount = 1,
}: ApplicationInboxTableProps) {
  const [filters, setFilters] = useState<ApplicationInboxFilters>(
    INITIAL_APPLICATION_INBOX_FILTERS,
  );
  const [inboxState, dispatchInboxState] = useReducer(
    reduceApplicationInboxReadState,
    {
      inbox: { groups, page, pageCount },
      errorMessage,
    },
  );
  const [isPending, startTransition] = useTransition();
  const initialLoad = useRef(true);
  const requestSequence = useRef(0);
  const [expandedCandidateId, setExpandedCandidateId] = useState<string | null>(
    null,
  );
  const [selectedCandidateIds, setSelectedCandidateIds] = useState<Set<string>>(
    new Set(),
  );
  const [activeSubmissionId, setActiveSubmissionId] = useState<string | null>(
    null,
  );

  const handleSubmissionUpdated = useCallback(
    (updated: {
      submissionId: string;
      hrNote: string | null;
      versionNo: number;
      hasApplication: boolean;
    }) => {
      const updatedGroups = inboxState.inbox.groups.map((group) => {
        const hasSub = group.submissions.some(
          (s) => s.submissionId === updated.submissionId,
        );
        if (!hasSub) return group;

        const updatedSubmissions = group.submissions.map((s) =>
          s.submissionId === updated.submissionId
            ? {
                ...s,
                hrNote: updated.hrNote,
                hasApplication: updated.hasApplication,
              }
            : s,
        );

        return {
          ...group,
          submissions: updatedSubmissions,
        };
      });

      dispatchInboxState({
        type: "loaded",
        inbox: {
          ...inboxState.inbox,
          groups: updatedGroups,
        },
      });
    },
    [inboxState.inbox],
  );

  const loadPage = useCallback(
    (nextPage: number, nextFilters: ApplicationInboxFilters) => {
      const sequence = ++requestSequence.current;
      startTransition(async () => {
        try {
          const nextInbox = await queryApplicationInbox({
            filters: nextFilters,
            page: nextPage,
          });
          if (sequence === requestSequence.current) {
            dispatchInboxState({ type: "loaded", inbox: nextInbox });
            setExpandedCandidateId(null);
          }
        } catch {
          if (sequence === requestSequence.current) {
            dispatchInboxState({
              type: "failed",
              message: "Không thể tải Phiếu Ứng tuyển. Vui lòng thử lại.",
            });
          }
        }
      });
    },
    [],
  );

  useEffect(() => {
    if (initialLoad.current) {
      initialLoad.current = false;
      return;
    }
    const timer = window.setTimeout(() => loadPage(1, filters), 250);
    return () => window.clearTimeout(timer);
  }, [filters, loadPage]);

  function updateFilters(patch: Partial<ApplicationInboxFilters>) {
    setFilters((current) => ({ ...current, ...patch }));
  }

  function toggleCandidate(candidateId: string) {
    setExpandedCandidateId((current) =>
      nextExpandedCandidateId(current, candidateId),
    );
  }

  function toggleSelectedCandidate(candidateId: string, selected: boolean) {
    setSelectedCandidateIds((current) => {
      const next = new Set(current);
      if (selected) next.add(candidateId);
      else next.delete(candidateId);
      return next;
    });
  }

  function resetFilters() {
    setFilters(INITIAL_APPLICATION_INBOX_FILTERS);
  }
  const displayedError = inboxState.errorMessage;
  const inbox = inboxState.inbox;

  return (
    <section className="application-inbox" aria-labelledby="inbox-heading">
      <div className="application-inbox__header">
        <div>
          <h2 id="inbox-heading">Quản lý Phiếu Ứng tuyển</h2>
          <p>
            Mỗi dòng là một Ứng viên; thông tin tóm tắt lấy từ phiếu mới nhất.
          </p>
        </div>
      </div>

      <form
        className="application-inbox__toolbar"
        aria-label="Tìm kiếm và lọc Phiếu Ứng tuyển"
        onSubmit={(event) => event.preventDefault()}
      >
        <div className="application-inbox__search">
          <label htmlFor="application-inbox-search">
            Tìm kiếm tên, email hoặc SĐT
          </label>
          <input
            id="application-inbox-search"
            type="search"
            value={filters.query}
            onChange={(event) => updateFilters({ query: event.target.value })}
            placeholder="Tìm tên, email, SĐT..."
          />
        </div>
        <label>
          Trạng thái phiếu
          <select
            value={filters.status}
            onChange={(event) =>
              updateFilters({
                status: event.target.value as ApplicationInboxFilters["status"],
              })
            }
          >
            <option value="ALL">Tất cả trạng thái</option>
            {Object.entries(SUBMISSION_STATUS_LABEL).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </label>
        <label>
          Từ ngày ứng tuyển
          <input
            type="date"
            value={filters.dateFrom}
            onChange={(event) =>
              updateFilters({ dateFrom: event.target.value })
            }
          />
        </label>
        <label>
          Đến ngày ứng tuyển
          <input
            type="date"
            value={filters.dateTo}
            onChange={(event) => updateFilters({ dateTo: event.target.value })}
          />
        </label>
        <label>
          Tài khoản Candidate
          <select
            value={filters.candidateActivity}
            onChange={(event) =>
              updateFilters({
                candidateActivity: event.target
                  .value as ApplicationInboxFilters["candidateActivity"],
              })
            }
          >
            <option value="ALL">Tất cả tài khoản</option>
            <option value="ACTIVE">Đang hoạt động</option>
            <option value="INACTIVE">Đã ngừng hoạt động</option>
          </select>
        </label>
        <label>
          Mới / đã đọc
          <select
            value={filters.newRead}
            onChange={(event) =>
              updateFilters({
                newRead: event.target
                  .value as ApplicationInboxFilters["newRead"],
              })
            }
          >
            <option value="ALL">Tất cả</option>
            <option value="NEW">Mới</option>
            <option value="READ">Đã đọc</option>
          </select>
        </label>
        <label>
          Application
          <select
            value={filters.application}
            onChange={(event) =>
              updateFilters({
                application: event.target
                  .value as ApplicationInboxFilters["application"],
              })
            }
          >
            <option value="ALL">Tất cả</option>
            <option value="HAS_APPLICATION">Đã có Application</option>
            <option value="NO_APPLICATION">Chưa có Application</option>
          </select>
        </label>
        {hasActiveFilters(filters) && (
          <button
            type="button"
            className="btn-secondary"
            onClick={resetFilters}
          >
            Xóa tìm kiếm và bộ lọc
          </button>
        )}
      </form>

      <p className="application-inbox__selection" aria-live="polite">
        {selectedCandidateIds.size} Candidate được chọn. Lựa chọn chỉ để theo
        dõi; chưa có thao tác thay đổi trong màn hình này.
      </p>

      <div className="application-inbox__table-scroll">
        <table className="application-inbox__table">
          <colgroup>
            {APPLICATION_INBOX_COLUMNS.map((column) => (
              <col
                key={column.key}
                className={`application-inbox__col--${column.key}`}
              />
            ))}
          </colgroup>
          <thead>
            <tr>
              {APPLICATION_INBOX_COLUMNS.map((column) => (
                <th key={column.key} scope="col">
                  {column.label}
                </th>
              ))}
            </tr>
          </thead>
          {loading || isPending ? (
            <tbody>
              <tr>
                <td colSpan={APPLICATION_INBOX_COLUMNS.length}>
                  <p
                    className="application-inbox__feedback"
                    role="status"
                    aria-live="polite"
                  >
                    Đang tải danh sách Candidate...
                  </p>
                </td>
              </tr>
            </tbody>
          ) : displayedError ? (
            <tbody>
              <tr>
                <td colSpan={APPLICATION_INBOX_COLUMNS.length}>
                  <p className="application-inbox__feedback" role="alert">
                    {displayedError}
                  </p>
                </td>
              </tr>
            </tbody>
          ) : inboxState.inbox.groups.length === 0 ? (
            <tbody>
              <tr>
                <td colSpan={APPLICATION_INBOX_COLUMNS.length}>
                  <p
                    className="application-inbox__feedback"
                    role="status"
                    aria-live="polite"
                  >
                    Không tìm thấy Candidate phù hợp với điều kiện hiện tại.
                  </p>
                </td>
              </tr>
            </tbody>
          ) : (
            <ApplicationInboxTableRows
              groups={inboxState.inbox.groups}
              expandedCandidateId={expandedCandidateId}
              selectedCandidateIds={selectedCandidateIds}
              onOpenSubmission={setActiveSubmissionId}
              onToggleCandidate={toggleCandidate}
              onToggleSelectedCandidate={toggleSelectedCandidate}
            />
          )}
        </table>
      </div>
      {!loading && !displayedError && (
        <nav
          className="application-inbox__pagination"
          aria-label="Phân trang Candidate"
        >
          <button
            type="button"
            className="btn-secondary"
            disabled={inbox.page === 1 || isPending}
            onClick={() => loadPage(inbox.page - 1, filters)}
          >
            Trang trước
          </button>
          <span aria-live="polite">
            Trang {inbox.page} / {inbox.pageCount}
          </span>
          <button
            type="button"
            className="btn-secondary"
            disabled={inbox.page === inbox.pageCount || isPending}
            onClick={() => loadPage(inbox.page + 1, filters)}
          >
            Trang sau
          </button>
        </nav>
      )}
      <SubmissionDetailDrawer
        submissionId={activeSubmissionId ?? ""}
        isOpen={activeSubmissionId !== null}
        onClose={() => setActiveSubmissionId(null)}
        onSubmissionUpdated={handleSubmissionUpdated}
      />
    </section>
  );
}
