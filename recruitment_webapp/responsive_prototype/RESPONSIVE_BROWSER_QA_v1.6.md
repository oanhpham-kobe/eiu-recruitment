# Responsive Browser QA v1.6

**TOTAL=47 PASS=47 FAIL=0**

Executed against the effective load chain through `responsive-v16.js` using headless Chromium.

| Result | Check | Detail |
|---|---|---|
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
| PASS | Bulk invalid member rolls back whole batch | NEW->NEW |
| PASS | Bulk valid Candidate updates latest Submission only |  |
| PASS | Candidate has no duplicated workflow status property |  |
| PASS | Inactivation changes Candidate lifecycle |  |
| PASS | Inactivation preserves Submission status |  |
| PASS | Aggregate report drawer has no generic Delete | Báo cáo phỏng vấn Current Interview: Vòng 2 Edit HR Note Đổi Report Status Ẩn khỏi Interviewer Xem PDF Tải PDF Report Status Theo dõi thêm Application outcom... |
| PASS | Aggregate drawer exposes required controls |  |
| PASS | Report Status writes Current Interview | FOLLOW_UP->REPORT_SUBMITTED |
| PASS | Report Status does not directly mutate Application status | FOLLOW_UP->FOLLOW_UP |
| PASS | Qualitative-only edit keeps Final Decision Source | ['u1', '24/05/2025 14:20']->['u1', '24/05/2025 14:20'] |
| PASS | New Candidate form blocks submit without CV |  |
| PASS | New Candidate form accepts staged CV ADD |  |
| PASS | EDIT staged DELETE cannot violate CV required |  |
| PASS | EDIT stages REPLACE |  |
| PASS | Cancel discards staged replacement |  |
| PASS | Cancel clears staged state |  |
| PASS | No JS/console errors | [] |
