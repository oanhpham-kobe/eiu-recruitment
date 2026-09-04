# Responsive Browser QA v1.9

**TOTAL=100 PASS=100 FAIL=0**

Executed against the effective load chain through `responsive-v19.js` using headless Chromium.

| Result | Check | Detail |
|---|---|---|
| PASS | Responsive README/VERSION authority v1.9 + Full v1.14 |  |
| PASS | no page overflow admin/applications 360x800 | 360/360 |
| PASS | no page overflow admin/hr-report 360x800 | 360/360 |
| PASS | no page overflow candidate/candidate-form 360x800 | 360/360 |
| PASS | no page overflow admin/applications 390x844 | 390/390 |
| PASS | no page overflow admin/hr-report 390x844 | 390/390 |
| PASS | no page overflow candidate/candidate-form 390x844 | 390/390 |
| PASS | no page overflow admin/applications 430x844 | 430/430 |
| PASS | no page overflow admin/hr-report 430x844 | 430/430 |
| PASS | no page overflow candidate/candidate-form 430x844 | 430/430 |
| PASS | no page overflow admin/applications 768x1024 | 768/768 |
| PASS | no page overflow admin/hr-report 768x1024 | 768/768 |
| PASS | no page overflow candidate/candidate-form 768x1024 | 768/768 |
| PASS | no page overflow admin/applications 1024x768 | 1024/1024 |
| PASS | no page overflow admin/hr-report 1024x768 | 1024/1024 |
| PASS | no page overflow candidate/candidate-form 1024x768 | 1024/1024 |
| PASS | no page overflow admin/applications 1280x800 | 1280/1280 |
| PASS | no page overflow admin/hr-report 1280x800 | 1280/1280 |
| PASS | no page overflow candidate/candidate-form 1280x800 | 1280/1280 |
| PASS | Phase1 admin nav hides FUTURE_HIDDEN | EIU \| EIU Recruitment System \| QUẢN LÝ TUYỂN DỤNG \| Phiếu ứng tuyển \| QUẢN LÝ QUY TRÌNH \| Interview \| Báo cáo phỏng vấn \| QUẢN TRỊ HỆ THỐNG \| Danh mụ... |
| PASS | Interviewer nav hides Home/Documents/Settings | EIU \| EIU Recruitment System \| PHỎNG VẤN CỦA TÔI \| Báo cáo phỏng vấn \| NT \| Nguyễn Thị An \| Interviewer |
| PASS | Candidate nav only applications | EIU \| EIU Recruitment System \| ỨNG VIÊN \| Phiếu ứng tuyển \| NT \| Nguyễn Thị An \| Ứng viên |
| PASS | Application Inbox bulk Delete removed |  |
| PASS | Application Inbox bulk candidate email removed |  |
| PASS | Inactive Candidate lifecycle shown separately | 	 \| Nguyễn Thị H \| 1 phiếu \| Candidate Inactive \| 	nguyenthih@gmail.com	22/12/1996	Nữ	0908 901 234	Đã đọc	Không phản hồi	 |
| PASS | Inactive Candidate preserves Submission workflow | Đã đọc |
| PASS | Demo Submission has no INACTIVE |  |
| PASS | Historical Submission statuses are read-only |  |
| PASS | Latest Submission menu only NEW READ | ['Mới', 'Đã đọc'] |
| PASS | Escape closes latest Submission menu |  |
| PASS | Escape restores focus |  |
| PASS | Inactive Candidate latest status remains clickable |  |
| PASS | Single manual status allowed for inactive Candidate | READ->NEW |
| PASS | Bulk inactive Candidate parity succeeds |  |
| PASS | Bulk active-Application member rolls back whole batch | READ->READ |
| PASS | Candidate has no duplicated workflow status property |  |
| PASS | Inactivation changes Candidate lifecycle |  |
| PASS | Inactivation preserves Submission status |  |
| PASS | Aggregate report drawer has no generic Delete | Báo cáo phỏng vấn Current Interview: Vòng 2 Edit HR Note Đổi Report Status Ẩn khỏi Interviewer Xem PDF Tải PDF Report Status Theo dõi thêm Application outcom... |
| PASS | Aggregate drawer exposes required controls |  |
| PASS | Report Status writes Current Interview | FOLLOW_UP->REPORT_SUBMITTED |
| PASS | Report Status does not directly mutate Application status | FOLLOW_UP->FOLLOW_UP |
| PASS | Qualitative-only edit keeps Final Decision Source | ['u1', '24/05/2025 14:20']->['u1', '24/05/2025 14:20'] |
| PASS | NEW Privacy starts unchecked |  |
| PASS | Education fields are not invented as required | 0 |
| PASS | Education permits zero rows |  |
| PASS | Education add remains repeatable |  |
| PASS | New Candidate form blocks submit without CV |  |
| PASS | Privacy explicit choice survives staged-file rerender |  |
| PASS | New Candidate form accepts staged CV ADD |  |
| PASS | EDIT staged DELETE cannot violate CV required |  |
| PASS | EDIT stages REPLACE |  |
| PASS | Cancel discards staged replacement |  |
| PASS | Cancel clears staged state |  |
| PASS | Schedule blocks same-Candidate overlap | ['Candidate'] |
| PASS | Schedule blocks Room overlap | ['Room'] |
| PASS | Schedule blocks Interviewer overlap | ['Interviewer'] |
| PASS | Adjacent end-start interval allowed | [] |
| PASS | CANCELLED round ignored by conflict engine | [] |
| PASS | Copy modal prefills source date | 2025-05-15 |
| PASS | Copy fills empty target Round1 | {'count': 1, 'no': 1, 'topic': '', 'date': '15/05/2025', 'start': '09:00', 'end': '10:00', 'location': 'Phòng Kỹ thuật 201 – EIU', 'prov': 'r11'} |
| PASS | Copy keeps Demo Topic blank | {'count': 1, 'no': 1, 'topic': '', 'date': '15/05/2025', 'start': '09:00', 'end': '10:00', 'location': 'Phòng Kỹ thuật 201 – EIU', 'prov': 'r11'} |
| PASS | Copy preserves source schedule logistics | {'count': 1, 'no': 1, 'topic': '', 'date': '15/05/2025', 'start': '09:00', 'end': '10:00', 'location': 'Phòng Kỹ thuật 201 – EIU', 'prov': 'r11'} |
| PASS | Copy records provenance | {'count': 1, 'no': 1, 'topic': '', 'date': '15/05/2025', 'start': '09:00', 'end': '10:00', 'location': 'Phòng Kỹ thuật 201 – EIU', 'prov': 'r11'} |
| PASS | Copied Round no longer structurally empty |  |
| PASS | Application modal uses exact SubmissionSelector | [{'value': 's1', 'text': 'Nguyễn Văn A — nguyenvana@gmail.com — Submitted: 20/05/2025 10:30 — Status: Đang xử lý'}, {'value': 's2', 'text': 'Nguyễn Văn A — n... |
| PASS | Same Candidate Submissions remain distinct | [{'value': 's1', 'text': 'Nguyễn Văn A — nguyenvana@gmail.com — Submitted: 20/05/2025 10:30 — Status: Đang xử lý'}, {'value': 's2', 'text': 'Nguyễn Văn A — n... |
| PASS | SubmissionSelector displays date and status | [{'value': 's1', 'text': 'Nguyễn Văn A — nguyenvana@gmail.com — Submitted: 20/05/2025 10:30 — Status: Đang xử lý'}, {'value': 's2', 'text': 'Nguyễn Văn A — n... |
| PASS | Application Save returns exact submission_id | ['s2', 'c1'] |
| PASS | Create blocks inactive selected Participant | 9->9 CURRENT_PARTICIPANT_INACTIVE_REASSIGN_REQUIRED: TS. Trần Minh Khoa |
| PASS | Copy blocks inactive prefilled Participant | 1->1 parts=u1,u2,u3 u1=False err=CURRENT_PARTICIPANT_INACTIVE_REASSIGN_REQUIRED: TS. Trần Minh Khoa |
| PASS | No page overflow admin/applications 375 | scroll=375 inner=375 |
| PASS | No page overflow admin/applications 430 | scroll=430 inner=430 |
| PASS | No page overflow admin/applications 768 | scroll=768 inner=768 |
| PASS | No page overflow admin/applications 1280 | scroll=1280 inner=1280 |
| PASS | No page overflow admin/interview 375 | scroll=375 inner=375 |
| PASS | No page overflow admin/interview 430 | scroll=430 inner=430 |
| PASS | No page overflow admin/interview 768 | scroll=768 inner=768 |
| PASS | No page overflow admin/interview 1280 | scroll=1280 inner=1280 |
| PASS | No page overflow admin/hr-report 375 | scroll=375 inner=375 |
| PASS | No page overflow admin/hr-report 430 | scroll=430 inner=430 |
| PASS | No page overflow admin/hr-report 768 | scroll=768 inner=768 |
| PASS | No page overflow admin/hr-report 1280 | scroll=1280 inner=1280 |
| PASS | No page overflow admin/permissions 375 | scroll=375 inner=375 |
| PASS | No page overflow admin/permissions 430 | scroll=430 inner=430 |
| PASS | No page overflow admin/permissions 768 | scroll=768 inner=768 |
| PASS | No page overflow admin/permissions 1280 | scroll=1280 inner=1280 |
| PASS | No page overflow candidate/candidate-form 375 | scroll=375 inner=375 |
| PASS | No page overflow candidate/candidate-form 430 | scroll=430 inner=430 |
| PASS | No page overflow candidate/candidate-form 768 | scroll=768 inner=768 |
| PASS | No page overflow candidate/candidate-form 1280 | scroll=1280 inner=1280 |
| PASS | No page overflow candidate/candidate-applications 375 | scroll=375 inner=375 |
| PASS | No page overflow candidate/candidate-applications 430 | scroll=430 inner=430 |
| PASS | No page overflow candidate/candidate-applications 768 | scroll=768 inner=768 |
| PASS | No page overflow candidate/candidate-applications 1280 | scroll=1280 inner=1280 |
| PASS | No page overflow interviewer/interviewer-report 375 | scroll=375 inner=375 |
| PASS | No page overflow interviewer/interviewer-report 430 | scroll=430 inner=430 |
| PASS | No page overflow interviewer/interviewer-report 768 | scroll=768 inner=768 |
| PASS | No page overflow interviewer/interviewer-report 1280 | scroll=1280 inner=1280 |
| PASS | No JS/console errors | [] |
