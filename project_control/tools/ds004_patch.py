from __future__ import annotations

from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
WEB = ROOT / "web"
SRC = WEB / "src"


def run(*args: str, cwd: Path = ROOT) -> None:
    subprocess.run(list(args), cwd=cwd, check=True)


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, got {count}")
    return text.replace(old, new, 1)


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")

# Candidate portal: converge control sizing and phone My Submissions presentation.
candidate_css_path = SRC / "styles/candidate-portal.css"
candidate_css = candidate_css_path.read_text(encoding="utf-8")
candidate_css = candidate_css.replace("font-size: 15px;", "font-size: 16px;")
candidate_css = replace_once(
    candidate_css,
    ".alert-dismiss-btn {\n  background: none;\n  border: none;\n  font-size: 16px;\n  cursor: pointer;\n  color: inherit;\n  padding: 0 4px;\n}",
    ".alert-dismiss-btn {\n  min-width: 44px;\n  min-height: 44px;\n  display: inline-grid;\n  place-items: center;\n  background: none;\n  border: none;\n  font-size: 20px;\n  cursor: pointer;\n  color: inherit;\n  padding: 0;\n}",
    "candidate alert dismiss target",
)
candidate_css = replace_once(
    candidate_css,
    ".btn-sm {\n  min-height: 36px;\n  padding: 4px 12px;\n  font-size: 14px;\n}\n",
    ".btn-sm {\n  min-height: 44px;\n  min-width: 44px;\n  padding: 8px 12px;\n  font-size: 16px;\n}\n\n@media (max-width: 640px) {\n  .portal-header,\n  .portal-user-meta,\n  .form-footer,\n  .action-buttons {\n    align-items: stretch;\n  }\n\n  .portal-user-meta,\n  .action-buttons {\n    width: 100%;\n  }\n\n  .action-buttons .btn,\n  .portal-user-meta .btn {\n    flex: 1 1 100%;\n  }\n\n  .table-responsive {\n    overflow: visible;\n  }\n\n  .submissions-table,\n  .submissions-table tbody,\n  .submissions-table tr,\n  .submissions-table td {\n    display: block;\n    width: 100%;\n  }\n\n  .submissions-table thead {\n    position: absolute;\n    width: 1px;\n    height: 1px;\n    padding: 0;\n    margin: -1px;\n    overflow: hidden;\n    clip: rect(0, 0, 0, 0);\n    white-space: nowrap;\n    border: 0;\n  }\n\n  .submissions-table tr {\n    margin-bottom: 12px;\n    border: 1px solid var(--line);\n    border-radius: var(--radius-card);\n    background: var(--surface);\n    overflow: hidden;\n  }\n\n  .submissions-table td {\n    display: grid;\n    grid-template-columns: minmax(116px, 38%) minmax(0, 1fr);\n    gap: 10px;\n    align-items: center;\n    padding: 10px 12px;\n  }\n\n  .submissions-table td::before {\n    content: attr(data-label);\n    color: var(--ink-600);\n    font-weight: var(--font-weight-semibold);\n  }\n\n  .submissions-table td .btn {\n    width: 100%;\n    min-width: 0;\n  }\n}\n",
    "candidate btn-sm and phone submissions",
)
write(candidate_css_path, candidate_css)

# Candidate submission rows expose visual mobile labels and remove undersized inline controls.
submissions_path = SRC / "components/candidate/SubmissionsList.tsx"
submissions = submissions_path.read_text(encoding="utf-8")
submissions = submissions.replace('<td>{index + 1}</td>', '<td data-label="STT">{index + 1}</td>')
submissions = submissions.replace(
    '<td>\n                      {formatDate(sub.submittedAt)} (v{sub.versionNo})\n                    </td>',
    '<td data-label="Ngày ứng tuyển / Submitted">\n                      {formatDate(sub.submittedAt)} (v{sub.versionNo})\n                    </td>',
)
submissions = submissions.replace('<td>\n                      <span className={`status-badge ${badgeClass}`}>', '<td data-label="Trạng thái / Status">\n                      <span className={`status-badge ${badgeClass}`}>')
submissions = submissions.replace('<td>\n                      {canEdit && onEditSubmission ? (', '<td data-label="Thao tác / Actions">\n                      {canEdit && onEditSubmission ? (')
submissions = submissions.replace('minHeight: "36px",\n                            padding: "4px 12px",\n                            fontSize: "14px",', 'minHeight: "44px",\n                            padding: "8px 12px",\n                            fontSize: "16px",')
submissions = submissions.replace('fontSize: "14px",\n                            color: "var(--ink-600, #68686b)",', 'fontSize: "16px",\n                            color: "var(--ink-600)",')
write(submissions_path, submissions)

# Application Inbox rows expose phone presentation labels without changing semantic table/business behavior.
rows_path = SRC / "components/inbox/ApplicationInboxTableRows.tsx"
rows = rows_path.read_text(encoding="utf-8")
parent_replacements = {
    '<td className="application-inbox__select-cell">': '<td className="application-inbox__select-cell" data-label="Chọn">',
    '<td>\n            {expandable ? (': '<td data-label="Candidate">\n            {expandable ? (',
    '<td className="wrap-anywhere">{group.email}</td>': '<td className="wrap-anywhere" data-label="Email">{group.email}</td>',
    '<td>{formatDateOfBirth(latest.dateOfBirth)}</td>': '<td data-label="Ngày sinh">{formatDateOfBirth(latest.dateOfBirth)}</td>',
    '<td>{formatGender(latest.gender)}</td>': '<td data-label="Giới tính">{formatGender(latest.gender)}</td>',
    '<td>{latest.phone ?? "—"}</td>': '<td data-label="SĐT">{latest.phone ?? "—"}</td>',
    '<td>\n            <span className={`status-badge ${STATUS_CLASS[latest.status]}`}>': '<td data-label="Trạng thái">\n            <span className={`status-badge ${STATUS_CLASS[latest.status]}`}>',
    '<td>{latest.hrNote ?? "—"}</td>': '<td data-label="HR Note">{latest.hrNote ?? "—"}</td>',
    '<td>\n            <button\n              type="button"\n              className="btn-secondary application-inbox__action-btn"': '<td data-label="Thao tác">\n            <button\n              type="button"\n              className="btn-secondary application-inbox__action-btn"',
}
for old, new in parent_replacements.items():
    if old not in rows:
        raise RuntimeError(f"application inbox parent anchor missing: {old[:50]}")
    rows = rows.replace(old, new, 1)

# Child rows: keep desktop grid alignment, provide meaningful phone labels, and hide structural placeholders on phone.
rows = rows.replace('<td aria-hidden="true" />\n              <td>', '<td aria-hidden="true" data-mobile-hidden="true" />\n              <td data-label="Loại">', 1)
rows = rows.replace('<td aria-hidden="true" />\n              <td>{formatSubmittedAt(submission.submittedAt)}</td>', '<td aria-hidden="true" data-mobile-hidden="true" />\n              <td data-label="Ngày ứng tuyển">{formatSubmittedAt(submission.submittedAt)}</td>', 1)
rows = rows.replace('<td aria-hidden="true" />\n              <td aria-hidden="true" />\n              <td>\n                <span', '<td aria-hidden="true" data-mobile-hidden="true" />\n              <td aria-hidden="true" data-mobile-hidden="true" />\n              <td data-label="Trạng thái">\n                <span', 1)
rows = rows.replace('<td>{submission.hrNote ?? "—"}</td>\n              <td>', '<td data-label="HR Note">{submission.hrNote ?? "—"}</td>\n              <td data-label="Thao tác">', 1)
write(rows_path, rows)

# Existing Internal drawer and Application Inbox phone presentation.
globals_path = SRC / "app/globals.css"
globals = globals_path.read_text(encoding="utf-8")
globals = replace_once(globals, "  max-width: 760px;", "  max-width: 820px;", "submission drawer width")
globals = replace_once(
    globals,
    ".submission-drawer__close-btn {\n  width: 36px;\n  height: 36px;",
    ".submission-drawer__close-btn {\n  width: 44px;\n  height: 44px;",
    "submission drawer close target",
)
phone_css = r'''

/* DS-004: phone presentation of the accepted Application Inbox semantic table. */
@media (max-width: 640px) {
  .application-inbox__table-scroll {
    overflow: visible;
    border: 0;
    box-shadow: none;
    background: transparent;
  }

  .application-inbox__table {
    display: block;
    width: 100%;
    min-width: 0;
  }

  .application-inbox__table colgroup,
  .application-inbox__table thead {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
  }

  .application-inbox__table tbody {
    display: grid;
    gap: 12px;
    margin-bottom: 12px;
  }

  .application-inbox__table tr {
    display: grid;
    width: 100%;
    border: 1px solid var(--line);
    border-radius: var(--radius-card);
    background: var(--surface);
    overflow: hidden;
  }

  .application-inbox__table td,
  .application-inbox__table td:first-child,
  .application-inbox__table td:nth-child(2) {
    position: static;
    display: grid;
    grid-template-columns: minmax(116px, 38%) minmax(0, 1fr);
    gap: 10px;
    align-items: center;
    width: auto;
    min-height: 44px;
    padding: 10px 12px;
    background: var(--surface);
    box-shadow: none;
  }

  .application-inbox__table td::before {
    content: attr(data-label);
    color: var(--ink-600);
    font-size: 16px;
    font-weight: var(--font-weight-semibold);
  }

  .application-inbox__table td[data-mobile-hidden="true"] {
    display: none;
  }

  .application-inbox__select-cell .application-inbox__selection-control {
    inline-size: 44px;
  }

  .application-inbox__expand-button,
  .application-inbox__action-btn {
    width: 100%;
  }

  .application-inbox__child-row td,
  .application-inbox__child-row td:first-child,
  .application-inbox__child-row td:nth-child(2) {
    background: var(--eiu-cream);
  }

  .submission-drawer {
    width: 100vw;
    max-width: none;
    height: 100dvh;
  }
}
'''
if "/* DS-004: phone presentation" not in globals:
    globals += phone_css
write(globals_path, globals)

# Focused static contract test.
test_path = SRC / "__tests__/design-responsive-convergence.test.ts"
write(test_path, r'''import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";

const read = (path: string) => readFileSync(new URL(path, import.meta.url), "utf8");

test("candidate and internal operational pages converge on responsive design contracts", () => {
  const candidateCss = read("../styles/candidate-portal.css");
  const submissions = read("../components/candidate/SubmissionsList.tsx");
  const inboxRows = read("../components/inbox/ApplicationInboxTableRows.tsx");
  const globals = read("../app/globals.css");

  assert.doesNotMatch(candidateCss, /font-size:\s*(14|15)px/);
  assert.match(candidateCss, /\.btn-sm[\s\S]*min-height:\s*44px[\s\S]*font-size:\s*16px/);
  assert.match(candidateCss, /@media \(max-width: 640px\)[\s\S]*\.submissions-table td::before/);
  assert.match(submissions, /data-label="Trạng thái \/ Status"/);
  assert.doesNotMatch(submissions, /minHeight: "36px"|fontSize: "14px"/);

  assert.match(globals, /\.submission-drawer[\s\S]*max-width:\s*820px/);
  assert.match(globals, /\.submission-drawer__close-btn[\s\S]*width:\s*44px[\s\S]*height:\s*44px/);
  assert.match(globals, /DS-004: phone presentation[\s\S]*\.application-inbox__table td::before/);
  assert.match(globals, /\.submission-drawer[\s\S]*width:\s*100vw[\s\S]*height:\s*100dvh/);
  assert.match(inboxRows, /data-label="Candidate"/);
  assert.match(inboxRows, /data-label="HR Note"/);
});
''')

# Focused verification: only domains changed by DS-004.
run("node", "--conditions", "react-server", "--test", "--import", "tsx", "src/__tests__/design-responsive-convergence.test.ts", "src/__tests__/candidate-portal.test.ts", "src/__tests__/application-inbox.test.ts", "src/__tests__/application-inbox-bulk-ui.test.ts", cwd=WEB)
run("npx", "biome", "check", "--write", "src/styles/candidate-portal.css", "src/components/candidate/SubmissionsList.tsx", "src/components/inbox/ApplicationInboxTableRows.tsx", "src/app/globals.css", "src/__tests__/design-responsive-convergence.test.ts", cwd=WEB)
run("npm", "run", "typecheck", cwd=WEB)
run("git", "diff", "--check", cwd=ROOT)

run("git", "add", "web/src/styles/candidate-portal.css", "web/src/components/candidate/SubmissionsList.tsx", "web/src/components/inbox/ApplicationInboxTableRows.tsx", "web/src/app/globals.css", "web/src/__tests__/design-responsive-convergence.test.ts", cwd=ROOT)
run("git", "commit", "-m", "feat(ds): converge existing responsive production pages", cwd=ROOT)
run("git", "push", "origin", "HEAD:oanhpham-kobe/DESIGN-SYSTEM-HARDENING-001", cwd=ROOT)
