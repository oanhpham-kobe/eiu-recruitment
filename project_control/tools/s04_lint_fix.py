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

stop = ' onClick={(event) => event.stopPropagation()}'
if text.count(stop) != 4:
    raise SystemExit(f"stopPropagation anchors: expected 4, found {text.count(stop)}")
text = text.replace(stop, "")

once(
    '<div className="interview-toolbar" aria-label="Thao tác Interview">',
    '<fieldset className="interview-toolbar"><legend className="sr-only">Thao tác Interview</legend>',
    "toolbar semantics",
)
once(
    '</div>\n\n      <div className="interview-filters" aria-label="Bộ lọc Interview">',
    '</fieldset>\n\n      <fieldset className="interview-filters"><legend className="sr-only">Bộ lọc Interview</legend>',
    "toolbar close and filter semantics",
)
once(
    '</div>\n\n      {feedback ? <AsyncStatus',
    '</fieldset>\n\n      {feedback ? <AsyncStatus',
    "filter close",
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

CSS = ROOT / "web/src/styles/interview.css"
css = CSS.read_text(encoding="utf-8")
anchor = ".interview-toolbar {\n  position: sticky;"
replacement = ".interview-toolbar {\n  margin: 0;\n  border: 0;\n  min-width: 0;\n  position: sticky;"
if css.count(anchor) != 1:
    raise SystemExit(f"toolbar css anchor: expected one, found {css.count(anchor)}")
css = css.replace(anchor, replacement, 1)
anchor = ".interview-filters {\n  display: flex;"
replacement = ".interview-filters {\n  margin: 0;\n  padding: 0;\n  border: 0;\n  min-width: 0;\n  display: flex;"
if css.count(anchor) != 1:
    raise SystemExit(f"filter css anchor: expected one, found {css.count(anchor)}")
css = css.replace(anchor, replacement, 1)
anchor = '''.interview-checkbox-label input,
.interview-copy-participants input[type="checkbox"] {
  width: 20px;
  height: 20px;
  min-height: 20px;
}'''
replacement = '''.interview-checkbox-label input,
.interview-copy-participants input[type="checkbox"] {
  width: 44px;
  height: 44px;
  min-height: 44px;
}'''
if css.count(anchor) != 1:
    raise SystemExit(f"checkbox size anchor: expected one, found {css.count(anchor)}")
css = css.replace(anchor, replacement, 1)
CSS.write_text(css.rstrip() + "\n", encoding="utf-8")

print("S04 lint/design blockers repaired")
