"use client";

import type React from "react";
import { useState } from "react";
import { Header } from "./Header";
import { MobileNavigation } from "./MobileNavigation";
import { Sidebar } from "./Sidebar";
import { SkipLink } from "./SkipLink";

export interface AppShellProps {
  children: React.ReactNode;
  title?: React.ReactNode;
  currentPath?: string;
  showInterviews?: boolean;
}

export function AppShell({
  children,
  title,
  currentPath = "/",
  showInterviews = true,
}: AppShellProps) {
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  return (
    <div className="shell">
      <SkipLink />
      <Sidebar currentPath={currentPath} showInterviews={showInterviews} />
      <MobileNavigation
        open={mobileNavOpen}
        currentPath={currentPath}
        showInterviews={showInterviews}
        onClose={() => setMobileNavOpen(false)}
      />
      <div className="shell-main">
        <Header
          title={title}
          mobileNavOpen={mobileNavOpen}
          onOpenNavigation={() => setMobileNavOpen(true)}
        />
        <main id="main-content" tabIndex={-1} className="content">
          {children}
        </main>
      </div>
    </div>
  );
}
