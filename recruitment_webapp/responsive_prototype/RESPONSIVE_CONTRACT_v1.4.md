# Responsive Contract v1.4 — UX-UAT Candidate Rules

Baseline: Full Handover v1.8 + Design System v1.7. These rules are prototype-level UX decisions pending final user visual approval.

## 1. Interview / Report status badge

For `Interview` and `Báo cáo phỏng vấn`:

- benchmark width: **144px**;
- benchmark label: **Đã gửi báo cáo**;
- Vietnamese short states stay one line when they fit;
- long English states such as `Awaiting Confirmation` wrap to two lines inside the same 144px badge;
- the badge must not stretch to fill the mobile value column;
- candidate/general status families are not forced to this width unless their own design contract says so.

## 2. Interview time

Canonical visual order in Interview and Interview Report views:

`14:00 – 15:30 · 20/05/2025`

Rules:
- time range first;
- date second;
- time range and date are individually non-breaking tokens;
- the pair may wrap only when the containing value area is genuinely too narrow;
- do not force date and time onto separate lines when the available width can display them together.

## 3. Mobile Report label width

On phone structured rows:
- `Thời gian phỏng vấn` / `Interview time` remains one line;
- HR Report label column target: **150px** on the audited phone range;
- the value column receives the remaining width and may wrap according to content.

## 4. Bulk selection interaction

- checkbox click must stop row propagation but must **not** call `preventDefault()`;
- selected state persists after render;
- toolbar actions read the same `selectedIds` state on desktop/tablet/mobile;
- there is no separate mobile business-selection implementation.

## 5. Button behavior in UX-UAT prototype

A visible enabled button in a core audited route must have one of:
1. a functional prototype flow that mutates sample state / opens an existing modal/drawer; or
2. an explicit prototype-feedback action explaining that persistence/backend behavior is outside prototype scope.

Silent/dead buttons are not acceptable for UX-UAT.
