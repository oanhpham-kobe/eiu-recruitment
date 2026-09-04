# CHANGELOG v1.15

- Added shared executable single/bulk Interview Schedule Status operational-transition guard and v1.10 browser QA.
- Changed Interview Upload Reservation FK to `ON DELETE RESTRICT`; added indexed parent reference and durable `storage_cleanup_queue`.
- Added Interview hard-delete reservation/temp-object cleanup ordering and acceptance coverage.
- Completed Bulk Candidate lifecycle side effects/audit and command-specific batch acceptance.
- Added single Interview Schedule Status to critical-control registry and critical-control browser-evidence checks.
- Updated Full/Technical baseline to v1.15, Responsive Prototype to v1.10, Review 93 and Gate 94.
