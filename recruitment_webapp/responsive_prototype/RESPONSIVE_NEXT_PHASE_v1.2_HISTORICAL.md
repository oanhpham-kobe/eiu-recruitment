# Responsive Next Phase — bắt đầu sau Desktop v1.1 PASS

## iPad / Tablet
- Thiết kế riêng cho 768–1199px, không chỉ scale desktop.
- Sidebar: collapsed rail hoặc off-canvas tùy portrait/landscape.
- Header giữ `VI | EN` ở top-right.
- Toolbar: wrap có thứ tự ưu tiên; primary action giữ visible.
- Data table: giữ semantic table cho HR; ẩn cột ít quan trọng theo page + horizontal scroll có kiểm soát.
- Drawer: 70–85vw landscape; full-width sheet ở portrait khi cần.
- Touch target >=44px.

## Mobile
- Candidate Portal ưu tiên mobile-first form/list.
- HR pages: navigation off-canvas; filter thành sheet; detail drawer thành full-screen sheet.
- Không ép toàn bộ bảng HR thành card. Mỗi page sẽ xác định `priority columns` và pattern phù hợp.
- Status badge/menu giữ 16px, touch target >=44px.
- `VI | EN` luôn truy cập được ở header/menu.

## Thứ tự wireframe responsive
1. Login
2. Candidate Form + Phiếu của tôi
3. Application Inbox
4. Interview
5. Interview Report — HR
6. Interview Report — Interviewer
7. Users & Permissions

Mỗi màn hình sẽ có ít nhất: desktop reference → iPad landscape → iPad portrait → mobile 390px.
