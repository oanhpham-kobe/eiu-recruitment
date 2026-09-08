from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    file = Path(path)
    text = file.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: expected one match, found {count}: {old[:120]!r}")
    file.write_text(text.replace(old, new, 1), encoding="utf-8")


path = "web/src/components/interview/InterviewPage.tsx"
replace_once(
    path,
    '''            <input
              type="checkbox"
              aria-label={`Chọn ${application.candidateName}`}
              checked={selectedInterviewId === selectId}
              onChange={(event) =>
                onSelect(event.target.checked ? selectId : null)
              }
            />''',
    '''            <label className="interview-select-target">
              <input
                type="checkbox"
                aria-label={`Chọn ${application.candidateName}`}
                checked={selectedInterviewId === selectId}
                onChange={(event) =>
                  onSelect(event.target.checked ? selectId : null)
                }
              />
            </label>''',
)
replace_once(
    path,
    '''                <input
                  type="checkbox"
                  aria-label={`Chọn Vòng ${round.roundNo}`}
                  checked={selectedInterviewId === round.interviewId}
                  onChange={(event) =>
                    onSelect(event.target.checked ? round.interviewId : null)
                  }
                />''',
    '''                <label className="interview-select-target">
                  <input
                    type="checkbox"
                    aria-label={`Chọn Vòng ${round.roundNo}`}
                    checked={selectedInterviewId === round.interviewId}
                    onChange={(event) =>
                      onSelect(event.target.checked ? round.interviewId : null)
                    }
                  />
                </label>''',
)

path = "web/src/styles/interview.css"
replace_once(
    path,
    '''.interview-table input[type="checkbox"] {
  width: 20px;
  height: 20px;
  margin: 2px auto;
}
''',
    '''.interview-select-target {
  display: inline-flex;
  width: 44px;
  height: 44px;
  align-items: center;
  justify-content: center;
  justify-self: center;
  cursor: pointer;
}

.interview-table input[type="checkbox"] {
  width: 20px;
  height: 20px;
  margin: 0;
}
''',
)

path = "web/src/__tests__/fixtures/interview-browser-acceptance-harness.tsx"
replace_once(
    path,
    '''                {INTERVIEW_COLUMNS.map((width, index) => (
                  <col key={`${width}-${index}`} style={{ width }} />
                ))}''',
    '''                {INTERVIEW_COLUMNS.map((width) => (
                  <col key={width} style={{ width }} />
                ))}''',
)
replace_once(
    path,
    '''          <div className="interview-detail-grid">
            <dt>Thời gian phỏng vấn</dt>
            <dd>14:00 – 15:30 · 20/05/2025</dd>
            <dt>Địa điểm</dt>
            <dd>Phòng A1.01</dd>
          </div>''',
    '''          <dl className="interview-detail-grid">
            <dt>Thời gian phỏng vấn</dt>
            <dd>14:00 – 15:30 · 20/05/2025</dd>
            <dt>Địa điểm</dt>
            <dd>Phòng A1.01</dd>
          </dl>''',
)
