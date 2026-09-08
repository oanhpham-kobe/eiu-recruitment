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

# The draft uses stopPropagation only to protect row-click behavior around real controls.
# Replace those handlers with event delegation on the parent row instead of making static
# wrapper/cell elements interactive.
stop = ' onClick={(event) => event.stopPropagation()}'
if text.count(stop) != 4:
    raise SystemExit(f"stopPropagation anchors: expected 4, found {text.count(stop)}")
text = text.replace(stop, "")

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
    'INTERVIEW_COLUMNS.map((width, index) => <col key={`${width}-${index}`} style={{ width }} />)',
    'INTERVIEW_COLUMNS.map((width) => <col key={width} style={{ width }} />)',
    "stable col keys",
)
once(
    '<tr className={`interview-application-row ${application.isActive ? "" : "is-inactive"}`} onClick={onToggle}>',
    '''<tr
        className={`interview-application-row ${application.isActive ? "" : "is-inactive"}`}
        onClick={(event) => {
          const target = event.target as HTMLElement;
          if (target.closest("button,input,a,select,textarea")) return;
          onToggle();
        }}
      >''',
    "row event delegation",
)

P.write_text(text.rstrip() + "\n", encoding="utf-8")
print("S04 lint blockers repaired")
