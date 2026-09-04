# 49. Technical Review – Vercel & Supabase Best Practices

> **STATUS: HISTORICAL / SUPERSEDED.** Superseded by later review resolutions and current v1.7 source. Old GAP/OWNER tables are historical only.

**Ngày rà soát:** 02/09/2026  
**Mục tiêu:** Đối soát Business Logic v1.2 + Design System hiện hành + external review với best practices hiện hành trong:

- `https://github.com/vercel-labs/agent-skills.git`
- `https://github.com/supabase/supabase.git`

Tài liệu này **không thay thế Business Logic v1.2**. Nó xác định các yêu cầu kỹ thuật cần khóa trước khi production coding/go-live.

## 1. Kết luận nhanh

| Nhóm | Kết quả |
|---|---|
| Business workflow | PASS – giữ nguyên phần đã freeze |
| Final Decision semantics | CHANGE REQUIRED – dùng `decision_updated_at`, không dùng generic `updated_at` |
| Schedule conflict | GAP – nên bổ sung Candidate conflict; owner confirmation còn mở |
| Database integrity | CHANGE REQUIRED |
| RLS / Grants / View security | CHANGE REQUIRED |
| Backend transaction contracts | MISSING → bổ sung trong v1.3 |
| Idempotency / concurrency | PARTIAL → bổ sung |
| Supabase Storage security | PARTIAL → bổ sung |
| Auth identity | PARTIAL → internal đã rõ; candidate method còn cần chốt |
| Email delivery | PARTIAL → bổ sung outbox/retry |
| Audit logging | PARTIAL → nâng thành mandatory security audit |
| Privacy / retention | OWNER / LEGAL DECISION REQUIRED |
| Vercel / React performance | PARTIAL → bổ sung implementation rules |
| Deployment / preview / backup | PARTIAL → bổ sung |
| Responsive | Candidate mobile = go-live requirement; internal HR desktop-first |

## 2. Những thay đổi kỹ thuật đã chấp nhận trong v1.3

### 2.1 Final Decision Source

Mỗi Interviewer vẫn có report độc lập. Hội đồng **không bắt buộc tất cả Interviewer nhập 3 trường final decision**.

Nghiệp vụ được hiểu như sau:

1. Hội đồng trao đổi và thống nhất.
2. Thông thường **01 Interviewer đại diện** điền 3 trường:
   - Conclusion;
   - Expected Specific Job Assigned;
   - Expected Recruitment Time.
3. Nếu một Interviewer khác sửa một trong 3 trường này sau đó, hệ thống hiểu đây là bản điều chỉnh mới sau trao đổi của hội đồng.
4. Chỉ khi một trong 3 field này thay đổi mới update:
   - `decision_updated_at`;
   - `decision_updated_by`.
5. Sửa các field đánh giá định tính không làm thay đổi Final Decision Source.
6. Current Final Decision Source = eligible report của Current Round có `decision_updated_at` mới nhất.
7. Cả 3 field final decision luôn lấy từ **cùng một report**; không merge giữa nhiều Interviewer.

### 2.2 Interview Report → Participant invariant

`interview_reports` tham chiếu trực tiếp `interview_participant_id` thay vì chỉ dựa trên `interviewer_user_id`.

Lợi ích:
- DB chứng minh report thuộc đúng người đã được chọn vào Interview Session;
- remove/re-add participant có thể restore/archive report an toàn;
- tránh service-role/backend ghi report cho người không thuộc hội đồng.

### 2.3 Application → Submission → Candidate

`candidate_id` không cần lưu lặp ở Application. Candidate được derive qua:

`Application → Submission → Candidate`.

Điều này loại bỏ trạng thái bất hợp lệ “Application của Candidate A nhưng dùng Submission của Candidate B”.

### 2.4 View security

Các view tính toán current round/outcome/final decision không được mặc định expose trực tiếp trong Data API.

- đặt ở schema `private` nếu có thể;
- nếu view cần exposed access thì phải `security_invoker=true`;
- grant/revoke explicit;
- không giả định view tự kế thừa RLS của underlying table khi creator có quyền cao.

### 2.5 Mutations dùng command/RPC

Các action nhiều side effect không được để frontend tự gọi nhiều lệnh DB rời rạc.

Ví dụ `create_application` phải atomic:

`authorize → validate → create/update Application → create Round 1 → recalc Submission → audit → commit`.

Chi tiết ở `37_BACKEND_COMMAND_CONTRACTS.md`.

## 3. Supabase best-practice alignment

### 3.1 Auth với Next.js

- Next.js App Router dùng cookie-based SSR auth.
- Dùng `@supabase/ssr` cho session nằm trong cookies.
- Server Actions/Route Handlers phải **authenticate + authorize như API endpoints**.
- Không tin role/permission do browser gửi lên.

### 3.2 RLS & Grants

- RLS bật trên toàn bộ table exposed chứa dữ liệu nghiệp vụ/cá nhân.
- RLS và `GRANT` là hai lớp khác nhau: phải cấu hình cả hai.
- Dùng `(select auth.uid())` trong policy nơi phù hợp và index các cột tham gia policy.
- Helper `SECURITY DEFINER`:
  - `set search_path = ''`;
  - nằm ở schema private nếu có thể;
  - tự kiểm tra identity/authorization;
  - `REVOKE EXECUTE` khỏi role không cần gọi.
- Không expose `service_role` / Supabase secret key trong browser.

### 3.3 Storage

- Hồ sơ tuyển dụng phải ở **private bucket**.
- Upload/download chịu RLS ở `storage.objects`.
- Bucket có `file_size_limit` + `allowed_mime_types` sau khi owner chốt whitelist.
- Không sửa/xóa trực tiếp metadata trong `storage` schema bằng SQL; dùng Storage API.
- Với tài liệu nhạy cảm, ưu tiên authenticated download/preview hoặc signed URL TTL ngắn. Không lưu signed URL dài hạn vào business table.

### 3.4 Branching / Vercel Preview

Supabase có integration để map Vercel preview deployment ↔ Supabase preview branch. Tuy nhiên tại thời điểm review có issue gần đây liên quan preview branch không bảo toàn một số grants/auth triggers trong một số tình huống. Vì vậy:

- không mặc định xem preview branch là security-equivalent với production;
- CI/UAT phải chạy security smoke tests trên mỗi preview/staging environment;
- staging final UAT nên dùng persistent isolated environment;
- production data không seed sang preview branch.

### 3.5 Backup

Database backup/PITR và Storage objects là hai concerns khác nhau.

Go-live runbook phải test:
- DB restore;
- Storage recovery/export strategy;
- consistency giữa metadata document và object thực tế.

## 4. Vercel / React best-practice alignment

### 4.1 Server-first architecture

- Next.js App Router.
- Server Components mặc định; chỉ dùng Client Components cho interaction thật sự cần JS.
- Giảm dữ liệu serialize từ Server → Client.
- Không lưu mutable request state ở module global.

### 4.2 Tránh waterfall

Các read độc lập nên chạy song song (`Promise.all`) hoặc cấu trúc component để fetch parallel.

Áp dụng cho:
- page header permissions + table data;
- lookup/master data độc lập;
- drawer metadata/documents khi phù hợp.

Không parallelize khi có dependency hoặc khi transaction cần thứ tự.

### 4.3 Server Actions

Mọi Server Action phải:

1. xác thực session;
2. authorize permission/context;
3. validate input;
4. gọi transactional command/RPC;
5. trả error code có cấu trúc.

Không coi việc “nút đã bị ẩn ở UI” là authorization.

### 4.4 Client bundle

- import trực tiếp component/module khi có thể, tránh barrel import lớn;
- heavy preview/PDF editor chỉ load khi mở;
- không ship permission tables, master catalogs, hoặc secrets không cần thiết xuống client;
- pagination/search server-side để tránh render list lớn.

### 4.5 URL state

Filter/sort/page/tab quan trọng nên phản ánh vào URL query params để:
- refresh không mất state;
- deep link được;
- back/forward đúng kỳ vọng.

Expanded row không bắt buộc lưu URL nếu làm UX quá nặng; row detail có thể dùng stable route/query param nếu cần share link.

## 5. External review: điểm nào giữ / điểm nào bỏ qua

### Giữ và xử lý

- Final Decision timestamp semantics.
- Candidate schedule conflict recommendation.
- View/RLS security.
- Application/Submission integrity.
- Unit/Team/Position consistency.
- Report ↔ Participant integrity.
- field-aware concurrency.
- backend command contracts.
- idempotency.
- DB constraints/version trigger.
- Root Admin bootstrap/protection.
- auth hardening.
- Storage security.
- service-role hard rule.
- privacy/retention.
- mandatory audit.
- email outbox/retry.
- NFR/backup/monitoring/rate limit/pagination/timezone.
- sync documentation status.

### Không mở lại vì business đã chốt

- Candidate bị khóa edit khi Submission chuyển khỏi `NEW` do HR đã mở/xử lý.
- Gender Phase 1 = Nam/Nữ.
- Email History UI có thể xóa record test/sai theo business rule; **security audit event của thao tác xóa vẫn immutable**.
- Một Application có nhiều rounds Phase 1.
- Current Round / PDF current round rule.
- Không scoring/rating.
- Hard-delete vs inactive business principle.

### Không chấp nhận như requirement hiện hành

- Tự thêm Quốc hiệu/Tiêu ngữ/Tên Hội đồng vào PDF khi chưa có template chính thức.

PDF phải bám đúng mẫu EIU được owner cung cấp sau.

## 6. References reviewed

- Vercel Agent Skills: `https://github.com/vercel-labs/agent-skills`
  - React Best Practices
  - Web Interface Guidelines
  - Vercel CLI / preview deployment guidance
- Supabase monorepo/docs: `https://github.com/supabase/supabase`
  - Next.js Auth / SSR
  - RLS / view security / grants
  - Storage access control/private buckets
  - branching/Vercel integration
  - production readiness/auth rate limits/backups

**Lưu ý:** Best practices có thể thay đổi theo thời gian; khi production coding bắt đầu, cần pin package versions và chạy lại technical audit trên code thật.
