# Kế hoạch phiếu nhận xét phỏng vấn và báo cáo tổng hợp

Ngày: 05/11/2026. Owner đã yêu cầu triển khai local và chọn mẫu nhận xét hiện có để chạy thử. Hành vi được chốt cho bản đầu nằm tại `recruitment_webapp/review_pack/101_INTERNAL_INTERVIEW_FEEDBACK.md` (CR-INTERVIEW-FEEDBACK-20261105); kế hoạch dưới đây giữ bối cảnh và các bước sau, không thay thế contract đó. Người nhận chỉ là nội bộ có tài khoản @eiu.edu.vn đã binding và được phân công.

Owner chọn hoàn thiện và kiểm thử local trước; cấu hình dịch vụ gửi email/quét virus thật sẽ làm sau. Không báo provider đã sẵn sàng từ kết quả local.

## 1. Kết quả người dùng cần

HR chọn ứng viên/vòng phỏng vấn, chọn mẫu câu hỏi và người nhận, bấm Gửi. Người nhận mở liên kết, đăng nhập Google Workspace, xem thông tin ứng viên được phép xem và trả lời theo mẫu. HR theo dõi ai đã gửi nhận xét, sau đó tạo bản tổng hợp theo mẫu báo cáo do Owner soạn. Bản tổng hợp giữ nguồn nhận xét từng người và cho phép HR duyệt trước khi phát hành.

Tính năng tạo bộ hồ sơ ứng viên để báo cáo được tách thành bước sau vì Owner sẽ mô tả riêng. Không tự suy diễn thành gom tất cả CV/tài liệu cá nhân hoặc gửi chúng trong email.

## 2. Luồng thao tác đề xuất

| Bước | Người thao tác | Hiển thị/kết quả |
|---|---|---|
| 1. Chuẩn bị phiếu | HR có quyền thích hợp | Chọn Application và đúng Interview round; chọn phiên bản mẫu câu hỏi, danh sách participant, hạn nộp nếu áp dụng; xem trước thông tin ứng viên sẽ được chia sẻ |
| 2. Gửi lời mời | HR | Tạo phiếu riêng cho từng participant và enqueue email trong cùng command có idempotency; UI phân biệt đã xếp hàng/gửi thành công/thất bại |
| 3. Mở phiếu | Người được mời | Đăng nhập @eiu.edu.vn; backend kiểm binding, active state, participant và visibility/context; không cấp quyền chỉ vì biết URL |
| 4. Điền nhận xét | Người được mời | Thông tin ứng viên tối thiểu ở đầu, nhóm câu hỏi bên dưới; lưu nháp, báo lỗi rõ, tiếp tục sau khi tải lại |
| 5. Gửi nhận xét | Người được mời | Kiểm tra câu hỏi bắt buộc theo mẫu, version và context; gửi nguyên tử; lưu thời điểm/người gửi/phiên bản phiếu |
| 6. Theo dõi | HR | Danh sách chưa mở/đang nháp/đã nộp/đã thu hồi; xem nội dung theo quyền; gửi nhắc có kiểm soát, không tự gửi hàng loạt ngoài yêu cầu |
| 7. Tổng hợp | HR | Khi đủ người theo danh sách đã xác nhận, tạo draft theo mẫu báo cáo tổng hợp; nhóm ý kiến theo câu hỏi/người nhận xét, giữ attribution |
| 8. Duyệt/phát hành | HR có quyền được duyệt | Xem trước, chỉnh phần nhận định chung theo quyền, chốt một phiên bản snapshot; tải định dạng được Owner yêu cầu sau khi thống nhất mẫu |

## 3. Bố cục trang nhận xét

1. Tên phiếu, ứng viên, vị trí ứng tuyển và vòng/ngày phỏng vấn.
2. Thông tin tóm tắt được allowlist: đề xuất họ tên, vị trí, đơn vị, thông tin trình độ/kinh nghiệm cần thiết nếu Owner duyệt. Không mặc định đưa địa chỉ, ngày sinh, số điện thoại, email cá nhân, ghi chú HR hoặc kết luận của người khác vào trang.
3. Hướng dẫn và hạn hoàn thành nếu có.
4. Từng nhóm câu hỏi với ô trả lời; câu bắt buộc đánh dấu theo template, không tự biến các field hiện tại thành bắt buộc.
5. Nút Lưu nháp và Gửi nhận xét; hiển thị trạng thái lưu, thay đổi chưa lưu, version conflict và xác nhận trước khi nộp.
6. Sau nộp: thông báo đã nộp, xem nội dung của chính mình; quyền sửa lại cần chính sách Owner chốt.

## 4. Tận dụng kiến trúc hiện có

- Giữ Next.js app + Supabase Auth/Postgres + private Storage; dùng session, participant/context authorization, email outbox, audit và optimistic version hiện có.
- Gắn phiếu vào **Application / Interview round / participant**. Không gắn chỉ Candidate: một người có nhiều Submission/Application và vòng phỏng vấn khác nhau.
- Liên kết email dẫn tới một route nội bộ cố định theo định danh phiếu, không chứa PII hay signed document URL. Sau login chỉ redirect tới đường dẫn nội bộ allowlist.
- Mẫu câu hỏi đã dùng phải có phiên bản bất biến. Sửa mẫu tạo phiên bản mới, không đổi câu hỏi của phiếu đã gửi/nộp.
- Một evaluator có một phiếu cho mỗi invitation/template-version trong round theo uniqueness được chốt. Double click Gửi hoặc retry không tạo phiếu/email trùng.
- Bản tổng hợp pin các response revision và template version đã dùng. Có người sửa lại sau đó thì bản tổng hợp cũ vẫn truy được provenance và được đánh dấu cần cập nhật khi thích hợp.
- Tổng hợp phiếu không tự thay Final Decision Source hoặc trạng thái tuyển dụng hiện tại; thay đổi quan hệ này cần Owner duyệt qua nguồn nghiệp vụ.
- Không triển khai microservice hoặc một generic workflow engine cho tính năng này.

## 5. Mô hình dữ liệu đề xuất, chưa phải schema được duyệt

| Khái niệm | Dữ liệu trách nhiệm |
|---|---|
| Mẫu phiếu và phiên bản | Tên, hướng dẫn, nhóm/câu hỏi, thứ tự, kiểu câu trả lời, bắt buộc/tùy chọn; published version bất biến |
| Đợt lấy nhận xét | Đúng Interview round, template version, người tạo, trạng thái, hạn nếu áp dụng, danh sách evaluator được xác nhận |
| Lời mời / phiếu cá nhân | Participant, người nhận, template version, trạng thái nháp/nộp/thu hồi, version; tham chiếu outbox cho delivery |
| Câu trả lời | Question identity/version, nội dung và revision; server xác minh tập câu hỏi hợp lệ, độ dài và quyền |
| Mẫu báo cáo tổng hợp | Vùng dữ liệu ứng viên, vị trí hiển thị ý kiến từng người, vùng HR tổng kết và placeholder được kiểm soát |
| Bản tổng hợp | Pinned template + response revisions + candidate snapshot, người duyệt, thời điểm, trạng thái và file output nếu có |

Tên bảng/RPC cụ thể chỉ chốt sau khi xem mẫu và đối chiếu domain model để tránh tạo hệ report thứ hai trùng lặp. Có thể mở rộng Report hiện tại nếu contract cho phép; không ép mẫu nhiều câu hỏi tùy biến vào 8 field hiện có làm mất ý nghĩa.

## 6. Các quyết định nghiệp vụ phải chốt từ mẫu

- Mẫu câu hỏi là nhận xét văn bản hay có lựa chọn khác? Contract hiện tại cấm tự bổ sung scoring/rating; chỉ mở nếu Owner đưa Change Request rõ ràng.
- Người chấm chỉ xem câu trả lời của mình hay được đọc ý kiến của nhau? Mặc định đề xuất chỉ xem của mình cho tới khi Owner duyệt chính sách khác.
- Sau nộp có được sửa? Đề xuất revision có kiểm soát, không ghi đè âm thầm. Cần thống nhất với final/writable và Current Round rules hiện có.
- Báo cáo chỉ ghép nguyên ý kiến hay HR viết phần tổng kết? Đề xuất ghép có attribution + HR duyệt; không mặc định dùng AI hoặc suy ra quyết định tuyển dụng bằng thuật toán.
- Thế nào là đủ phiếu khi participant bị gỡ, tài khoản bị khóa, hạn đã hết hoặc HR cần báo cáo chưa đủ người? Không tự loại evaluator khỏi denominator để tạo trạng thái hoàn thành giả.
- Định dạng báo cáo Owner cần: mẫu Word/PDF hoặc trang in. Mẫu chính thức và bộ hồ sơ ứng viên sẽ do Owner cung cấp, không tự tạo official layout.

## 7. Bảo mật và transaction

- Domain email không đủ để cấp quyền: phải là tài khoản nội bộ đã binding, active và được phân công đúng round/participant.
- Tất cả read/save/submit/aggregate/export checks ở backend/database; raw table/projection/RPC/download đều phải bảo vệ tương đương.
- Thu hồi lời mời, gỡ participant, ẩn session, inactive parent/user và chuyển final status phải chặn write theo contract; kiểm lại quyền sau khi chờ lock.
- Lưu nháp dùng version; nộp là transaction nguyên tử với audit. Khi submit đua với revoke/finalize, chỉ một kết quả hợp lệ được commit.
- Không gửi nội dung hồ sơ/tài liệu nhạy cảm trong email; email chỉ chứa nội dung mời tối thiểu và link đăng nhập.
- Template chỉ hỗ trợ placeholder và nội dung đã kiểm soát, không chạy script/HTML tùy ý; file export lưu private, có authorization/audit trước truy cập.

## 8. Kế hoạch triển khai theo lát cắt

| Mốc | Công việc | Điều kiện hoàn thành |
|---|---|---|
| A. Sẵn sàng nền | Đóng deadlock/lỗi audit hiện tại; thống nhất report precedence và mail runtime | Current workflows qua regression thật; không dựa vào test self-assertion hoặc queue-only delivery |
| B. Source & template contract | Owner đưa mẫu câu hỏi và báo cáo; chốt visibility, sửa sau nộp, completion policy | Mẫu ví dụ và acceptance được duyệt, cập nhật canonical source theo controlled change |
| C. Một phiếu trọn luồng | Một HR gửi cho một participant, login, xem tối thiểu Candidate, lưu nháp, nộp | Browser + real-role SQL + concurrency proof trên synthetic nonprod |
| D. Hội đồng nhiều người | Danh sách evaluator, delivery status, nhắc gửi, revoke/reopen policies | Không trùng lời mời, không lộ chéo, completion chính xác qua lifecycle changes |
| E. Tổng hợp theo mẫu | Bản draft đúng template, từng ý kiến có nguồn, HR duyệt, version snapshot | Kiểm field mapping với mẫu Owner, không bỏ ý kiến hoặc tự suy kết luận |
| F. Xuất báo cáo | Output theo định dạng Owner chốt, private access và audit | Kiểm nội dung/file, quyền HR/Interviewer và historical/current semantics |
| G. Bộ hồ sơ ứng viên | Scope riêng sau mô tả của Owner | Xác định nguồn tài liệu, bộ field, format, người nhận, privacy/retention và provenance |

## 9. Acceptance bắt buộc

1. Người A không mở/sửa được phiếu của B bằng URL hoặc direct RPC/table access.
2. User cùng domain nhưng chưa được phân công vẫn bị từ chối; inactive/unbound user bị từ chối.
3. Mẫu đổi sau khi gửi không làm thay câu hỏi của phiếu cũ; bản báo cáo cũ vẫn tái dựng được.
4. Hai tab sửa cùng phiếu không mất dữ liệu do stale overwrite; submit/revoke/lifecycle races không deadlock hay partial commit.
5. Double click/retry Gửi không nhân bản phiếu/outbox; email lỗi hiển thị đúng, không báo đã gửi khi mới queued.
6. Tổng hợp đúng tập người chấm được chốt, đúng thứ tự câu hỏi và nguồn; không nhầm Submission/Application/round.
7. Từ chối truy cập không tiết lộ HR notes/private metadata; tài liệu nếu được duyệt phải đi qua cùng private-access boundary.
8. Keyboard, nhãn trường, focus, error summary và responsive form dùng được trên browser thực.
9. Luồng hiện tại không bị thay đổi ngầm bởi phiếu mới; scoring/conclusion/source rules chỉ đổi khi Owner duyệt.

Tài liệu này là kế hoạch cho feature mới. Các lựa chọn chưa được Owner xác nhận không phải implementation authority, và không tự cấp phép gửi email, thay cấu hình hosted hoặc triển khai production.
