import fs from "node:fs";
import path from "node:path";

function validateControlPlaneConsistency() {
  const root = path.resolve(__dirname, "..");
  const errors: string[] = [];

  const autonomyRunStatePath = path.join(root, "project_control/AUTONOMY_RUN_STATE.yaml");
  const autonomyContent = fs.readFileSync(autonomyRunStatePath, "utf-8");

  const sliceRegistryPath = path.join(root, "project_control/SLICE_REGISTRY.yaml");
  const sliceContent = fs.readFileSync(sliceRegistryPath, "utf-8");

  const taskRegistryPath = path.join(root, "project_control/TASK_REGISTRY.yaml");
  const taskContent = fs.readFileSync(taskRegistryPath, "utf-8");

  // Helper: extract lines belonging strictly to a specific 2-space indented block under 'slices:'
  function getSliceBlock(content: string, sliceId: string): string | null {
    const lines = content.split("\n");
    let inSlices = false;
    let inTarget = false;
    const blockLines: string[] = [];

    for (const line of lines) {
      if (/^slices:\s*$/m.test(line)) {
        inSlices = true;
        continue;
      }
      if (inSlices && /^[a-zA-Z0-9_]+:\s*$/m.test(line)) {
        break; // Next top-level key
      }
      if (inSlices) {
        if (new RegExp(`^\\s{2}${sliceId}:`).test(line)) {
          inTarget = true;
          blockLines.push(line);
          continue;
        }
        if (inTarget) {
          // If another 2-space key starts, target block ended
          if (/^\s{2}[a-zA-Z0-9_-]+:/.test(line)) {
            break;
          }
          blockLines.push(line);
        }
      }
    }
    return blockLines.length > 0 ? blockLines.join("\n") : null;
  }

  // Helper: extract lines belonging strictly to a specific 2-space indented block under 'tasks:'
  function getTaskBlock(content: string, taskId: string): string | null {
    const lines = content.split("\n");
    let inTasks = false;
    let inTarget = false;
    const blockLines: string[] = [];

    for (const line of lines) {
      if (/^tasks:\s*$/m.test(line)) {
        inTasks = true;
        continue;
      }
      if (inTasks && /^[a-zA-Z0-9_]+:\s*$/m.test(line)) {
        break; // Next top-level key
      }
      if (inTasks) {
        if (new RegExp(`^\\s{2}${taskId}:`).test(line)) {
          inTarget = true;
          blockLines.push(line);
          continue;
        }
        if (inTarget) {
          if (/^\s{2}[a-zA-Z0-9_-]+:/.test(line)) {
            break;
          }
          blockLines.push(line);
        }
      }
    }
    return blockLines.length > 0 ? blockLines.join("\n") : null;
  }

  // Check 1: Strict block-scoped check for SLICE-00 through SLICE-03 in SLICE_REGISTRY
  for (const s of ["SLICE-00", "SLICE-01", "SLICE-02", "SLICE-03"]) {
    const block = getSliceBlock(sliceContent, s);
    if (!block) {
      errors.push(`Contradiction: Block for ${s} not found under slices: in SLICE_REGISTRY.yaml`);
      continue;
    }
    const statusMatch = block.match(/status:\s*([A-Za-z0-9_]+)/);
    if (!statusMatch || statusMatch[1] !== "DONE") {
      errors.push(`Contradiction in SLICE_REGISTRY: ${s} status is '${statusMatch ? statusMatch[1] : "NOT_FOUND"}', expected 'DONE'`);
    }
  }

  // Check 2: Strict block-scoped check for all 21 tasks in TASK_REGISTRY
  const expectedDoneTasks = [
    "TASK-S00-001", "TASK-S00-002", "TASK-S00-003", "TASK-S00-004", "TASK-S00-005",
    "TASK-S01-001", "TASK-S01-002", "TASK-S01-003", "TASK-S01-004", "TASK-S01-005",
    "TASK-S02-001", "TASK-S02-002", "TASK-S02-003", "TASK-S02-004", "TASK-S02-005",
    "TASK-S03-001", "TASK-S03-002", "TASK-S03-003", "TASK-S03-004", "TASK-S03-005", "TASK-S03-006"
  ];

  for (const t of expectedDoneTasks) {
    const block = getTaskBlock(taskContent, t);
    if (!block) {
      errors.push(`Contradiction: Block for ${t} not found under tasks: in TASK_REGISTRY.yaml`);
      continue;
    }
    const statusMatch = block.match(/status:\s*([A-Za-z0-9_]+)/);
    if (!statusMatch || statusMatch[1] !== "DONE") {
      errors.push(`Contradiction in TASK_REGISTRY: ${t} status is '${statusMatch ? statusMatch[1] : "NOT_FOUND"}', expected 'DONE'`);
    }
  }

  // Check 3: Check for duplicate top-level keys in AUTONOMY_RUN_STATE
  const keys = autonomyContent.split("\n")
    .filter(l => /^[a-z0-9_]+:/i.test(l))
    .map(l => l.split(":")[0].trim());
  const duplicateKeys = keys.filter((item, index) => keys.indexOf(item) !== index);
  if (duplicateKeys.length > 0) {
    errors.push(`Duplicate top-level key(s) in AUTONOMY_RUN_STATE: ${duplicateKeys.join(", ")}`);
  }

  // Check 4: Explicit activation hold in AUTONOMY_RUN_STATE
  if (!autonomyContent.includes("status: HELD_FOR_GOVERNANCE_REVIEW")) {
    errors.push("Contradiction: slice_04_execution status must be HELD_FOR_GOVERNANCE_REVIEW during governance maintenance");
  }
  if (!autonomyContent.includes("auto_advance: PENDING_OWNER_REVIEW")) {
    errors.push("Contradiction: auto_advance must be PENDING_OWNER_REVIEW during governance maintenance");
  }

  if (errors.length > 0) {
    console.error("CONTROL PLANE CONSISTENCY CHECK: FAIL");
    for (const err of errors) console.error(" - " + err);
    process.exit(1);
  } else {
    console.log("CONTROL PLANE CONSISTENCY CHECK: PASS");
    console.log(" - Verified SLICE-00 through SLICE-03 all DONE via strict block-scoped parser");
    console.log(" - Verified all 21 tasks (S00-001 to S03-006) all DONE in TASK_REGISTRY via strict block-scoped parser");
    console.log(" - Verified no duplicate top-level keys in AUTONOMY_RUN_STATE");
    console.log(" - Verified explicit activation hold in AUTONOMY_RUN_STATE");
    console.log(" - Zero contradictions detected between live registries");
  }
}

validateControlPlaneConsistency();
