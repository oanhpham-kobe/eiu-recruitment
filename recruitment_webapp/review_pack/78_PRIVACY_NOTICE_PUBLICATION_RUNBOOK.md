# 78. Privacy Notice Publication / Current-Switch Runbook — CURRENT

## Scope
Phase 1 maintenance/deployment-only procedure. No Candidate/HR UI publishes Privacy Notice versions. Published content is immutable.

## Preconditions
- authorized Root/operations change with recorded approval;
- exact VI/EN content and SHA-256 hash reviewed;
- unique new `notice_version`;
- `effective_from` agreed;
- rollback operator identified.

## Publish future version
1. Insert new immutable version with `is_current=false`.
2. Verify stored content/hash and `effective_from`.
3. Do **not** unset the existing effective current notice early.
4. Record audit/change evidence.

## Current switch at/after effective time
Single DB transaction:
1. lock current notice row + target version;
2. assert target exists and `effective_from <= transaction_now`;
3. assert target content/hash metadata unchanged;
4. set old `is_current=false`;
5. set target `is_current=true`;
6. query exactly one current/effective notice; if not exactly one, raise/rollback;
7. commit + audit.

Because both pointer changes are in one transaction, a failure rolls back to the former current notice. A future-effective version is never made current before its effective time.

## Verification
- start a NEW and EDIT Form Session; both pin target notice;
- arbitrary client notice version rejected;
- prior acknowledgements still resolve immutable old version;
- `AC-PRIV-PUBLISH-01` passes.

## Rollback
If a post-switch operational issue requires rollback, switch current pointer back to the prior already-published effective version in one audited transaction. Never edit published content in place.
