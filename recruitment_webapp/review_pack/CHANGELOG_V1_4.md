# Full Handover v1.4 Changelog

## Owner decisions closed
- Candidate schedule overlap = BLOCK.
- Candidate Auth = Email OTP.
- Upload = PDF/Word/PPT/PNG/JPEG, max 5 files, max 5 MB/file.
- Current business retention = no automatic purge; capacity warning then upgrade or local archive + explicit purge.
- Official PDF pixel template deferred.

## External Review v2 hardening
- default-full HR but granular permission semantics; read-only `submissions.view`;
- Root-only bound identity rebind;
- separate Interview Note / HR Report Note;
- mandatory schedule resource locking and shared conflict engine;
- explicit Reactivate command;
- Candidate first-login provisioning;
- explicit Submission selection for Application;
- schema/master-data conformance and null-team fix;
- effective active parent semantics;
- unused Application empty-Round1 delete rule;
- expanded backend command coverage and DTO allowlists;
- logical document versioning + two-phase upload;
- at-least-once email semantics + leakage guard;
- privacy acknowledgement;
- WCAG contrast/table/nav fixes in Design System v1.3;
- fail-closed package validator;
- measurable NFR baseline and search/indexing strategy;
- pinned dependency/auth regression requirement.
