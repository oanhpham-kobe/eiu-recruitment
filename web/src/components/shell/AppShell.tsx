"use client";

import type React from "react";
import { useState } from "react";
import { Header } from "./Header";
import { LocaleProvider } from "./LocaleProvider";
import { MobileNavigation } from "./MobileNavigation";
import type { NavItem } from "./navigation";
import { Sidebar } from "./Sidebar";
import { SkipLink } from "./SkipLink";

export interface AppShellProps {
  children: React.ReactNode;
  title?: React.ReactNode;
  currentPath?: string;
  navItems?: readonly NavItem[];
}

function AppShellContent({
  children,
  title,
  currentPath = "/",
  navItems = [],
}: AppShellProps) {
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  return (
    <div className="shell">
      <SkipLink />
      <Sidebar currentPath={currentPath} navItems={navItems} />
      <MobileNavigation
        open={mobileNavOpen}
        currentPath={currentPath}
        navItems={navItems}
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

export function AppShell(props: AppShellProps) {
  return (
    <LocaleProvider>
      <AppShellContent {...props} />
    </LocaleProvider>
  );
}
