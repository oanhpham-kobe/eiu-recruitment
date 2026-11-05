# Hồ sơ phong cách UniCouncil / EIU

Tham chiếu từ các quyết định trong UniCouncil Scheduler và bộ review 30/10/2026; đóng gói ngày 04/11/2026. Dùng để tái hiện phong cách khi được yêu cầu. Hồ sơ không khẳng định bản review đã triển khai lên production.

## Nhận diện và token

| Vai trò | Giá trị tham chiếu |
|---|---|
| Primary / tiêu đề | `#144069` |
| Sidebar | `#102F4D` |
| Gold trang trí | `#A78656` |
| Canvas bản review | `#F8F6F1` |
| Surface | `#FFFFFF` |
| Text chính | `#303033` |
| Text phụ | `#58595B` |
| Viền phân nhóm | `#EAE2D6` |
| Viền control bản review | `#8A8F94` |
| Skeleton | `#E3E9ED` |
| Tiêu đề display PC | Crimson Pro, khoảng 30/38 px |
| UI, nội dung, label | Be Vietnam Pro, từ 14 px |
| Input mobile | Be Vietnam Pro, từ 16 px |
| Icon | Heroicons, cùng nét và tỷ lệ toàn app |
| Khoảng cách | 4, 8, 12, 16, 20, 24, 32 px |
| Radius | 8, 12, 16 px theo tầng component |

Màu trạng thái dùng semantic token chung: đang xử lý/chờ duyệt xanh dương; điều chỉnh cam; đã duyệt xanh lá; hoàn thành xám; hủy/nguy hiểm đỏ. Nền nhẹ, chữ và chấm tròn cùng semantic hue. Dùng token hiện hành của dự án cho giá trị cụ thể và kiểm tra tương phản trên nền thực; không suy ra quyền từ màu.

Chỉnh sửa cam; Hủy trong popup Trình lãnh đạo/Yêu cầu bổ sung và Hủy yêu cầu đỏ. Xác nhận nghiệp vụ dùng primary. Giữ logo đúng tỷ lệ; không dùng gold cho chữ nhỏ trên nền sáng nếu thiếu tương phản.

## Quy ước sản phẩm khi sửa UniCouncil

- PC 5 dòng/trang; mobile 4 thẻ/trang, chỉ danh sách cuộn. Phân trang ghim đáy. Sidebar có vị trí workspace thống nhất giữa các page.
- Thành phần tham dự PC tối đa 3 dòng. Mobile 1–2 dòng phù hợp số dòng nội dung cuộc họp; vượt giới hạn thì ellipsis và xem đầy đủ trong chi tiết.
- Mã dạng `20260910-001`: ngày tạo và STT trong ngày trên toàn bộ đơn vị. Mã ở popup trên một dòng riêng, nội dung yêu cầu bên dưới.
- Nhãn “Ngày đề xuất”, “Lịch chờ duyệt”, “Lịch chính thức” căn trái trên mobile. Không hiển thị giá trị thiếu ở thẻ hoặc dấu phân cách thừa.
- Form “Thông tin đề xuất cuộc họp”, nhãn “Đơn vị”, “Họ và tên”, “Email”. Không thêm lại “Loại cuộc họp”. Tên người đăng ký lấy từ hồ sơ đã xác thực theo triển khai hiện hành.
- Đơn vị chọn một, tìm kiếm và nhập ngoài gợi ý theo luồng đã chốt. Thành phần chọn nhiều; gợi ý theo `unit_name_vi`, chip/tóm tắt theo `short_name_vi` khi có, giữ nguyên phần nhập tự do.
- Requester không đề xuất địa điểm và không thấy đơn vị đăng ký trong chi tiết theo chốt hiện tại. Địa điểm hiển thị khi assistant đã chốt. Assistant không sửa ngày đề xuất gốc của requester; ngày trình lãnh đạo là trường riêng.
- Popup Trình lãnh đạo chọn nhiều lãnh đạo, ngày trình bắt buộc; giờ và địa điểm hiển thị nhưng không bắt buộc. Lãnh đạo sắp xếp theo `staff_id` bằng quy tắc hiện hành của ứng dụng.
- Requester/assistant thấy lịch chờ duyệt khi assistant đã chọn ngày để trình; leader thấy ngày assistant trình, không thêm lịch đề xuất gốc của requester vào phần duyệt.
- Lãnh đạo thấy “Chờ duyệt” thay “Mới”. Quyền duyệt theo danh sách lãnh đạo được trình; admin có phạm vi/hành động theo backend. Duyệt, hủy yêu cầu đã duyệt và hủy duyệt phải bám kiểm tra quyền hiện hành; không suy diễn quyền mới từ hồ sơ này.
- Hoàn thành dùng xám ở mọi role; không tính vào KPI Đã duyệt và mặc định ẩn khỏi lịch, bật qua bộ lọc để xem lại. Tự chuyển hoàn thành theo ngày/giờ phải theo logic và múi giờ sản phẩm.
- Lịch mặc định chính thức. Filter: Trạng thái → Lãnh đạo → Đơn vị. Mobile giữ số cuộc họp, bật lịch chờ duyệt và tất cả lãnh đạo cùng một dòng khi đủ chỗ; không giảm chữ dưới 14 px để ép vừa.
- Điều hướng thời gian dùng `‹ Hôm nay ›`: trước/sau theo ngày, tuần hoặc tháng đang xem; Hôm nay đưa về kỳ hiện tại. Nhãn ngày/khoảng ngày hoặc tháng/năm hiện cạnh cụm hay xuống dòng trên mobile; chọn lịch và filter thời gian theo [time-filters.md](time-filters.md).
- PDF/ảnh có thể preview trong lớp riêng có X; Office được upload và tải xuống, không bắt buộc chuyển PDF. Chỉ có mắt khi preview được. Mức 25 MB/tệp là tham chiếu đã thảo luận; luôn đối chiếu giới hạn backend trước khi ghi lên UI.
- Thông báo lưu: “Đã lưu”.

Quy ước nghiệp vụ trên chỉ dành cho UniCouncil. Khi có quyết định mới, cập nhật theo quyết định đó; mâu thuẫn ảnh hưởng quyền/dữ liệu cần làm rõ. Không mang role, đơn vị, trạng thái hay giới hạn tệp này sang app khác máy móc.

## Ảnh và Figma tham chiếu

- [Mobile: Requests / Admin / Calendar](../assets/mobile-overview.png)
- [Popup: Trình lãnh đạo / Yêu cầu bổ sung / Hủy](../assets/popup-overview.png)
- [Tải / rỗng / lỗi tài liệu](../assets/feedback-overview.png)
- [Page 09 review trong Figma](https://www.figma.com/design/UNDek7yMuyZMQukeHROhle?node-id=438-913)

Ảnh hướng dẫn thị giác, không phải kiểm thử thiết bị hay source UI. Khi dùng cho app khác, không sao chép logo EIU, tên, email, mã hoặc dữ liệu mẫu trong ảnh. Dựng lại bằng component và dữ liệu của dự án mới.
