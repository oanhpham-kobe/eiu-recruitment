from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = ROOT / "web/src/components/interview/InterviewPage.tsx"
text = P.read_text(encoding="utf-8")


def once(old: str, new: str, label: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    text = text.replace(old, new, 1)

once("  type InterviewParticipant,\n", "", "unused participant import")
once(
    '      <div\n        className={`interview-status-menu interview-status-menu--${round.scheduleStatus.toLowerCase()}`}\n        onClick={(event) => event.stopPropagation()}\n      >',
    '      <div\n        className={`interview-status-menu interview-status-menu--${round.scheduleStatus.toLowerCase()}`}\n      >',
    "status wrapper click",
)
once(
    '<div className="interview-toolbar" aria-label="Thao tác Interview">',
    '<div className="interview-toolbar" role="group" aria-label="Thao tác Interview">',
    "toolbar semantics",
)
once(
    '<div className="interview-filters" aria-label="Bộ lọc Interview">',
    '<div className="interview-filters" role="group" aria-label="Bộ lọc Interview">',
    "filter semantics",
)
once(
    '{INTERVIEW_COLUMNS.map((width, index) => (\n              <col key={`${width}-${index}`} style={{ width }} />\n            ))}',
    '{INTERVIEW_COLUMNS.map((width) => (\n              <col key={width} style={{ width }} />\n            ))}',
    "stable col keys",
)
once(
    '<tr className={`interview-application-row ${application.isActive ? "" : "is-inactive"}`} onClick={onToggle}>',
    '''<tr\n        className={`interview-application-row ${application.isActive ? "" : "is-inactive"}`}\n        onClick={(event) => {\n          const target = event.target as HTMLElement;\n          if (target.closest("button,input,a,select,textarea")) return;\n          onToggle();\n        }}\n      >''',
    "row event delegation",
)
once(
    '<td data-label="Chọn" onClick={(event) => event.stopPropagation()}>',
    '<td data-label="Chọn">',
    "checkbox cell click",
)
once(
    '<td\n          data-label="Trạng thái"\n          onClick={(event) => event.stopPropagation()}\n        >',
    '<td data-label="Trạng thái">',
    "status cell click",
)
once(
    '<td data-label="Action" onClick={(event) => event.stopPropagation()}>',
    '<td data-label="Action">',
    "action cell click",
)
P.write_text(text.rstrip() + "\n", encoding="utf-8")
print("S04 lint blockers repaired")
