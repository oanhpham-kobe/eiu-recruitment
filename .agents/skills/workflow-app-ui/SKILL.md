---
name: workflow-app-ui
description: Design and refine internal workflow apps with fluid desktop/mobile layouts, aligned tables and badges, filters, forms, calendars and admin screens. Use when building business UI or reusing the user's UniCouncil interface conventions across apps.
---

# Workflow App UI

Tạo giao diện nghiệp vụ trang trọng, dễ đọc, có mật độ thông tin hợp lý trên PC và mobile. Áp dụng trong phạm vi người dùng yêu cầu; giữ thương hiệu, tính năng và quyền nghiệp vụ của dự án đang làm.

## Chọn ngữ cảnh

- Đọc component, token, bản thiết kế và tài liệu chốt liên quan trước khi sửa. Tái sử dụng hệ thống sẵn có; tập trung vào những điểm thiếu hoặc chưa đồng bộ.
- Đọc [references/layout-and-alignment.md](references/layout-and-alignment.md) khi làm bố cục, kích thước responsive, lề hai bên, bảng, badge hoặc trạng thái tương tác. Đây là quy tắc trình bày dùng chung cho cả PC và mobile.
- Dùng [references/workflow-patterns.md](references/workflow-patterns.md) khi làm danh sách, form, chi tiết, popup, lịch hoặc Admin; chỉ đọc phần liên quan.
- Dùng [references/time-filters.md](references/time-filters.md) khi làm bộ lọc thời gian, lịch chọn ngày/khoảng ngày hoặc cụm điều hướng `‹ Hôm nay ›`.
- Dùng [references/unicouncil-profile.md](references/unicouncil-profile.md) khi làm UniCouncil hoặc khi người dùng muốn phong cách EIU giống app mẫu. Với app mới, chuyển nguyên tắc bố cục sang thương hiệu của app đó. Không tự gán logo EIU, dữ liệu hay quyền của UniCouncil.
- Nếu làm trên Figma, dùng workflow Figma có sẵn trong môi trường; tạo layer chỉnh sửa được, component, text và auto-layout. Ảnh mẫu chỉ để đối chiếu, không dùng làm nền thay thế toàn bộ UI.

## Nền tảng cần giữ

**Dễ đọc.** Chữ UI chức năng tối thiểu 14 px, gồm nhãn, badge, metadata, bộ lọc, phân trang, nút và gợi ý. Ô nhập trên mobile dùng ít nhất 16 px để hạn chế browser tự zoom khi focus; vẫn cho phép pinch zoom. Logo và nội dung tài liệu gốc không phải chữ UI để ép theo quy tắc này. Dùng khoảng 20–24 px line-height cho chữ 14–16 px.

**Rõ thứ bậc.** Giữ màu thương hiệu làm điểm tựa; nền trung tính và màu trạng thái tiết chế. Chữ phụ vẫn phải đọc rõ trên nền thực tế. Kiểm tra tương phản của chữ, trạng thái focus và đường biên ô nhập; không dùng màu trang trí làm chữ nhỏ nếu tương phản không đủ. Màu không thay thế nhãn hoặc icon trạng thái.

**Token và component chung.** Dùng một nguồn cho font, màu semantic, khoảng cách, radius, badge, input, button, pagination, dialog và tài liệu. Chọn dải khoảng cách có nhịp, ví dụ 4/8/12/16/20/24/32 px. Ưu tiên sửa component/token gốc thay vì CSS ghi đè riêng từng page hoặc role. Cùng trạng thái dùng cùng chữ, chấm tròn, icon, màu nền và viền.

**Căn chỉnh nhất quán.** Chữ và nhóm icon/chấm + chữ trong badge căn giữa ngang và dọc bên trong badge. Bản thân badge đặt theo lề cột hoặc nhóm chứa nó, không tự căn giữa cả cột. Header bảng và nội dung từng cột mặc định căn trái, cùng trục bắt đầu, cùng padding và cùng định nghĩa độ rộng cột. Các dòng không tự chia cột độc lập. Ngoại lệ căn chỉnh phải có mục đích rõ và đồng bộ cả header lẫn dữ liệu cột đó.

**Hành động phân biệt được.** Một hành động chính nổi bật trong mỗi nhóm. Với phong cách này, Chỉnh sửa dùng cam; Hủy yêu cầu, xóa hoặc thao tác hủy dùng đỏ; xác nhận nghiệp vụ thông thường dùng màu chính. Phân biệt việc đóng popup với việc hủy dữ liệu bằng nhãn rõ ràng. Khi dự án có quy ước màu được chốt khác, giữ quy ước đó. Nút icon có tên truy cập và vùng chạm khoảng 44×44 px khi bố cục cho phép.

## Khung responsive

- Co giãn theo chiều rộng vùng làm việc trên **cả PC, tablet và mobile**, kể cả khi kéo nhỏ/phóng lớn cửa sổ PC. Bảng, filter và footer dùng chiều rộng khả dụng sau sidebar và lề hai bên, không neo nguyên màn hình vào một chiều rộng bản vẽ cố định.
- PC phân bổ cột linh hoạt: mã, trạng thái và thao tác có đủ chỗ; cột nội dung nhận phần còn lại. Giữ nhãn ngắn, ngày, mã và tiêu đề cột cần đọc liền trên một dòng bằng cách cấp đủ chỗ; không ép `nowrap` cho toàn bộ nội dung. Khi thiếu chỗ, sắp lại toolbar, thu sidebar hoặc đổi bố cục theo nội dung trước khi gây tràn ngang.
- Mobile ưu tiên vừa chiều ngang, không đưa nguyên bảng PC có `min-width` lớn vào khung nhỏ. Chuyển sang thẻ, trường xếp dọc hoặc bố cục lịch phù hợp. Dùng `min-width: 0` cho phần tử flex/grid có thể co, chọn wrap hoặc ellipsis theo loại nội dung.
- Lề ngoài trái/phải (page gutter) đối xứng theo bảng dưới; tiêu đề nội dung, filter, bảng/thẻ và phân trang dùng cùng trục lề. Gutter tính từ mép vùng làm việc, không tính thêm bề rộng sidebar; padding bên trong thẻ là token riêng, tránh cộng lề lặp qua nhiều wrapper.
- Với danh sách nghiệp vụ, cố định header, cụm từ filter trở lên và phân trang ở đáy khung app tại mức zoom bình thường. Chỉ vùng thẻ/dòng cuộn dọc bằng chuột hoặc cảm ứng. Trong flex/grid, vùng cuộn cần được phép co (`min-height: 0`), không để nội dung kéo dài toàn trang.
- Tính chiều cao theo viewport động và vùng an toàn thiết bị; xử lý browser toolbar và bàn phím ảo. Khi zoom hoặc chiều cao rất thấp, ưu tiên nội dung và focus vẫn truy cập được thay vì cắt mất điều khiển. Không tắt zoom để che lỗi layout.
- Bộ lọc mobile giữ phần thường dùng gọn và dễ thấy; đưa lựa chọn còn lại vào sheet/popup có tìm kiếm khi cần. Phần lọc đang áp dụng phải nhận biết và đặt lại được.
- Số thẻ mỗi trang và số thẻ nhìn thấy đồng thời là hai khái niệm khác nhau. Không cam kết toàn bộ thẻ của một trang nằm vừa một màn hình.

Lề ngoài mặc định khi dự án chưa có token khác được chốt (CSS px):

| Khung màn hình tham chiếu | Gutter mỗi bên |
|---|---:|
| Mobile nhỏ ≤360 px | 12 px |
| Mobile 361–767 px | 16 px |
| Tablet 768–1023 px | 20–24 px |
| PC ≥1024 px | 24–32 px |

Đây là giá trị khởi đầu, không phải breakpoint cứng cho mọi component. Chọn một token cụ thể trong mỗi khoảng và dùng đồng bộ toàn app; điều chỉnh theo chiều rộng nội dung thực tế. Bảng nghiệp vụ có thể dùng hết khung; form hoặc nội dung đọc dài có thể giới hạn chiều rộng và căn giữa. Không giới hạn mọi màn hình vào cùng một max-width.

## Trạng thái và tính nhất quán

- Tính khoảng hiển thị, tổng kết quả, số trang và trạng thái nút từ cùng dữ liệu đã lọc. Không thêm số 0 trước số thống kê. Trạng thái không có kết quả phải có số đếm phù hợp.
- KPI đếm theo ý nghĩa nghiệp vụ đã chốt; không tự gộp các trạng thái có mục đích khác nhau. Bộ lọc mặc định và cách truy cập lịch sử phải rõ.
- Giữ cùng shell, vị trí workspace, ngôn ngữ, cách lọc và bố cục chi tiết giữa các role. Khác biệt nằm ở dữ liệu được xem và hành động được phép. Không mở rộng quyền chỉ vì tái sử dụng giao diện.
- Có trạng thái tải, rỗng ban đầu, không khớp bộ lọc, lỗi tải, đang lưu và thành công khi luồng cần. Lỗi kết nối có thể thử lại; tài liệu đã xóa hoặc không còn quyền cần đường quay lại/liên hệ phù hợp.
- Thông báo thành công không che phân trang hoặc hành động quan trọng. Khóa gửi trùng trong khi xử lý; hiển thị tiến độ khi upload đủ lâu để cần phản hồi.

## Hoàn tất trong phạm vi được giao

Kiểm tra màn hình đại diện ở PC và mobile, cả khi kéo đổi kích thước liên tục, nội dung dài, nhãn ngôn ngữ khác, bộ lọc đang bật, trạng thái rỗng/lỗi và các role liên quan. Soát ảnh render thực tế, trục căn cột, badge, gutter và hành vi cuộn/focus/đóng popup; kiểm tra cấu trúc không thay cho thử browser. Đọc hướng dẫn framework của repo trước khi viết code.

Khi người dùng yêu cầu duyệt hình trước, tạo bản review riêng, giữ bản chốt cũ, gửi ảnh xuất thật cùng link Figma hoặc preview. Chỉ triển khai/merge/deploy trong phạm vi đã được cho phép; việc gọi skill không tự cấp quyền deploy. Nếu nhiệm vụ đã cho phép thực hiện, tiếp tục làm và kiểm tra đầy đủ mà không thêm vòng xác nhận không cần thiết.

Kết quả nói rõ đã sửa gì, đã kiểm tra ở đâu và đang là thiết kế, preview hay production. Không ghi quyết định mới là “đã chốt” khi người dùng chưa chốt.
