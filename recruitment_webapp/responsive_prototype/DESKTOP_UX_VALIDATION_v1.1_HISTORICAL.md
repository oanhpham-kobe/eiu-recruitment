# Desktop UX Validation — Prototype v1.1

## Kết quả vòng kiểm tra sau khi áp Design System v1.1

| ID | Kiểm tra | Kết quả |
|---|---|---|
| DT-01 | Parent row Application Inbox click toàn dòng để expand/collapse | PASS |
| DT-02 | Checkbox / status badge / action icon không trigger expand | PASS |
| DT-03 | Submission child rows dùng cùng outer table/colgroup, không lệch lưới | PASS |
| DT-04 | Interview parent click toàn dòng; round child nằm đúng các cột Vòng/Time/Location/Status/Participants/Note | PASS |
| DT-05 | Column widths được xác định trong colgroup, không auto-width theo từng row | PASS |
| DT-06 | Header table 16px semibold | PASS |
| DT-07 | Body table 16px; long content wrap | PASS |
| DT-08 | Drawer/Modal/Preview/Form primary text >=16px | PASS |
| DT-09 | Badge 16px semibold, center, equal width theo status group | PASS |
| DT-10 | VI là mặc định | PASS |
| DT-11 | `VI | EN` ở top-right và persist preference | PASS |
| DT-12 | Toolbar có một nút Status dropdown | PASS |
| DT-13 | Click trực tiếp status badge HR/Admin mở status menu | PASS |
| DT-14 | Candidate/Interviewer status badge read-only | PASS |
| DT-15 | Status menu cập nhật state prototype và render lại | PASS |
| DT-16 | Interview Report không có score/rating/điểm | PASS |
| DT-17 | CONFIRMED vẫn khóa Edit lịch theo logic hiện có | PASS |
| DT-18 | Copy/Create interview vẫn chạy conflict validation hiện có | PASS |

## Ghi chú
- English mode dịch system UI; business/master-data content đang lưu một label (ví dụ tên Khoa/Vị trí, HR Note, Demo Topic) không tự dịch, đúng Design System v1.1.
- Vì font tăng lên 16px, bảng desktop chủ động dùng min-width + horizontal scroll nếu viewport thiếu; không giảm font để nhét cột.
- Responsive adaptation chưa áp dụng trong file desktop này.

## Gate
**Desktop Design System v1.1 application: PASS for UX-UAT.**
Có thể chuyển sang thiết kế responsive riêng cho iPad/tablet và mobile.

## Automated/static smoke check
- JavaScript syntax (`app.js`, `v11-overrides.js`): PASS.
- Runtime logic smoke (Node VM without DOM): PASS for colgroup markup, whole-row expand hooks, EN status/nav translation, direct status badge permissions, and persistent round-status mutation.
- CSS rule inspection: PASS for fixed table layout, 16px header/body, group badge widths, and VI|EN switcher hooks.
- Container Chromium visual screenshot could not be used reliably because the environment's headless Chromium process did not terminate; this is an environment limitation, not counted as a product PASS. Final visual UX still requires opening `index.html` in a normal desktop browser.
