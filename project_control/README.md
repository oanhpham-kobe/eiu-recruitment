# PROJECT_CONTROL_BOOTSTRAP

Implementation-governance bootstrap and reference template for **EIU Recruitment**.

- **Authority:** EIU Full Handover v1.17 remains the authority for WHAT the system must do.
- **Role:** These bootstrap files represent the pre-implementation reference template and historical repository bootstrap. Live implementation state and registries are maintained under `project_control/` (`AUTONOMY_RUN_STATE.yaml`, `TASK_REGISTRY.yaml`, `SLICE_REGISTRY.yaml`, `EVIDENCE_INDEX.yaml`, `CURRENT_STATE.md`).
- **Repository Lifecycle:** Git baseline was established on branch `main` at `D:/orca/recruitment` (`cdd1ea3e`). Slices 00 through 03 are complete and verified on remote CI. Slices 04 through 08 are planned.
- **Portability:** Full Handover source files resolve relative to `SOURCE_ROOT = recruitment_webapp`.
- **Session Protocol:** Future sessions must run Resume Project Protocol and inspect live `project_control/` before modifying code.
