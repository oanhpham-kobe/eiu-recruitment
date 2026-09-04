import type React from "react";
import { Header } from "./Header";
import { Sidebar } from "./Sidebar";
import { SkipLink } from "./SkipLink";

export interface AppShellProps {
  children: React.ReactNode;
  title?: React.ReactNode;
  currentPath?: string;
}

export function AppShell({ children, title, currentPath }: AppShellProps) {
  return (
    <div className="shell">
      <SkipLink />
      <Sidebar currentPath={currentPath} />
      <div className="shell-main">
        <Header title={title} />
        <main id="main-content" tabIndex={-1} className="content">
          {children}
        </main>
      </div>
    </div>
  );
}
