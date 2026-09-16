import { useState } from "react";
import { createRoot } from "react-dom/client";
import { EmailHistoryDrawer } from "@/components/interview/EmailHistoryDrawer";
import { EmailPreviewDialog } from "@/components/interview/EmailPreviewDialog";
import "@/app/globals.css";
import "@/styles/interview.css";
import {
  EMAIL_HARNESS_CONTEXT,
  getEmailHarnessSnapshot,
  makeNextEnqueueStale,
  resetEmailHarnessState,
} from "./email-ui-actions.mock";

function Harness() {
  const [previewOpen, setPreviewOpen] = useState(false);
  const [historyOpen, setHistoryOpen] = useState(false);
  const [queuedCount, setQueuedCount] = useState(0);
  const [snapshot, setSnapshot] = useState(getEmailHarnessSnapshot());

  const refreshSnapshot = () => setSnapshot(getEmailHarnessSnapshot());

  return (
    <main data-harness-ready="email-ui">
      <button type="button" data-testid="open-preview" onClick={() => setPreviewOpen(true)}>
        Open preview
      </button>
      <button
        type="button"
        data-testid="open-stale-preview"
        onClick={() => {
          makeNextEnqueueStale();
          setPreviewOpen(true);
        }}
      >
        Open stale preview
      </button>
      <button type="button" data-testid="open-history" onClick={() => setHistoryOpen(true)}>
        Open history
      </button>
      <div data-testid="queued-count">{queuedCount}</div>
      <pre data-testid="snapshot">{JSON.stringify(snapshot)}</pre>

      <EmailPreviewDialog
        open={previewOpen}
        emailType="INTERVIEW_INVITATION"
        interviewId={EMAIL_HARNESS_CONTEXT.interviewId}
        applicationId={EMAIL_HARNESS_CONTEXT.applicationId}
        submissionId={EMAIL_HARNESS_CONTEXT.submissionId}
        contextSummary="Vòng 1 · 09:00"
        onClose={() => setPreviewOpen(false)}
        onQueued={() => {
          setQueuedCount((count) => count + 1);
          refreshSnapshot();
        }}
      />

      <EmailHistoryDrawer
        open={historyOpen}
        interviewId={EMAIL_HARNESS_CONTEXT.interviewId}
        title="Candidate — Vòng 1"
        canDelete
        onClose={() => setHistoryOpen(false)}
      />
    </main>
  );
}

resetEmailHarnessState();
const rootElement = document.getElementById("root");
if (!rootElement) throw new Error("Email UI behavior harness root is missing");
createRoot(rootElement).render(<Harness />);
