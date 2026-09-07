import type React from "react";
import { SkipLink } from "./SkipLink";

export function CandidateShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="candidate-shell">
      <SkipLink />
      <main id="main-content" tabIndex={-1} className="candidate-shell__main">
        {children}
      </main>
    </div>
  );
}
