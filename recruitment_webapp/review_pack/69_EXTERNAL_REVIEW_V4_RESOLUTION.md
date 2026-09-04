# 69. External Review v4 Resolution — Full Review v1.5 / DS v1.4

> **STATUS: HISTORICAL / SUPERSEDED.** Historical resolution log; superseded by External Review v5 resolution and v1.7 current source.

Source: `EIU_Recruitment_Full_Review_v1.5_DS_v1.4.md` supplied by owner on 02/09/2026. Business Logic Core v1.2 remains FROZEN. Owner approved all proposed technical amendments; no new business decision remains.

## P0 resolutions
- Candidate Reactivate + no active Application → `READ` lifecycle exception.
- HR Submission document mutation, Interview document delete, Email History delete and all coverage commands are explicit trusted commands.
- Email wording distinguishes idempotent logical enqueue from at-least-once provider delivery.
- Directory manager cannot lifecycle HR-role/Root targets; HR target lifecycle is Root-only.

## P1 resolutions
- Candidate recreated Auth ID safe-rebind predicate specified.
- File-only Submission document Save bumps aggregate version.
- Privacy Notice is server-published and pinned to Form Session.
- Email Outbox/History supports exact `submission_id` trace.
- Application Reactivate pre-checks duplicate identity; only Current Round operational.
- Room added to structural history protection.
- Rate-limit, Web Security and Export/Archive/Purge normative docs added.
- Exact hard-delete permissions added; HR owner moved to Application management.
- App spec conflict engine includes Application Reactivate.
- Hard-delete/open-session cleanup ordering specified.
- Machine-readable command registry + semantic validation added.

## Design/docs resolutions
- Drawer legacy 55vw rule removed package-wide from current source.
- HR Inbox gains FileList/FilePreview-related components.
- Acceptance IDs unique.
- Current version labels advanced to Technical v1.6 / Design System v1.5.
- COMPONENTS numbering fixed; Sidebar current header fixed.
- Open-ended bulk wording removed.
- All-in-One has deterministic generator + equality check.
