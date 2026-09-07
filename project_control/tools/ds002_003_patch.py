from __future__ import annotations

from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
WEB = ROOT / "web"
SRC = WEB / "src"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8", newline="\n")


def run(*args: str, cwd: Path = ROOT) -> None:
    subprocess.run(list(args), cwd=cwd, check=True)

# ============================================================================
# DS-002 — explicit shell responsibilities + responsive internal navigation
# ============================================================================
write(SRC / "components/shell/CandidateShell.tsx", r'''
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
''')

write(SRC / "components/shell/MobileNavigation.tsx", r'''
"use client";

import { useEffect, useRef } from "react";
import { createPortal } from "react-dom";
import { DEFAULT_NAV_ITEMS } from "./Sidebar";

interface MobileNavigationProps {
  open: boolean;
  currentPath: string;
  onClose: () => void;
}

const FOCUSABLE =
  'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';

export function MobileNavigation({ open, currentPath, onClose }: MobileNavigationProps) {
  const panelRef = useRef<HTMLElement>(null);
  const closeRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!open) return;
    const appRoot = document.getElementById("app-root");
    const previousOverflow = document.body.style.overflow;
    appRoot?.setAttribute("inert", "");
    appRoot?.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "hidden";
    closeRef.current?.focus();

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.preventDefault();
        onClose();
        return;
      }
      if (event.key !== "Tab" || !panelRef.current) return;
      const focusable = Array.from(
        panelRef.current.querySelectorAll<HTMLElement>(FOCUSABLE),
      );
      if (focusable.length === 0) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    };
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("keydown", onKeyDown);
      appRoot?.removeAttribute("inert");
      appRoot?.removeAttribute("aria-hidden");
      document.body.style.overflow = previousOverflow;
      document.getElementById("internal-nav-trigger")?.focus();
    };
  }, [open, onClose]);

  if (!open || typeof document === "undefined") return null;

  return createPortal(
    <div className="mobile-nav-layer">
      <button
        type="button"
        className="mobile-nav-backdrop"
        aria-label="Đóng menu / Close menu"
        onClick={onClose}
      />
      <aside
        ref={panelRef}
        className="mobile-nav-panel"
        role="dialog"
        aria-modal="true"
        aria-label="Điều hướng nội bộ / Internal navigation"
      >
        <div className="mobile-nav-header">
          <strong>EIU Recruitment</strong>
          <button ref={closeRef} type="button" className="mobile-nav-close" onClick={onClose}>
            <span aria-hidden="true">×</span>
            <span className="sr-only">Đóng menu / Close menu</span>
          </button>
        </div>
        <nav aria-label="Menu chức năng / Navigation menu">
          <ul className="mobile-nav-list">
            {DEFAULT_NAV_ITEMS.map((item) => (
              <li key={item.href}>
                <a
                  href={item.href}
                  aria-current={currentPath === item.href ? "page" : undefined}
                  onClick={onClose}
                >
                  {item.label}
                </a>
              </li>
            ))}
          </ul>
        </nav>
        <div className="mobile-nav-user">
          <strong>Quản trị viên / Admin</strong>
          <span>Phòng Nhân sự / HR Department</span>
        </div>
      </aside>
    </div>,
    document.body,
  );
}
''')

write(SRC / "components/shell/AppShell.tsx", r'''
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
}

export function AppShell({ children, title, currentPath = "/" }: AppShellProps) {
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  return (
    <div className="shell">
      <SkipLink />
      <Sidebar currentPath={currentPath} />
      <MobileNavigation
        open={mobileNavOpen}
        currentPath={currentPath}
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
''')

write(SRC / "components/shell/Header.tsx", r'''
import type React from "react";

export interface HeaderProps {
  title?: React.ReactNode;
  mobileNavOpen?: boolean;
  onOpenNavigation?: () => void;
}

export function Header({
  title = "Hệ thống Tuyển dụng EIU / EIU Recruitment",
  mobileNavOpen = false,
  onOpenNavigation,
}: HeaderProps) {
  return (
    <header className="topbar">
      <button
        id="internal-nav-trigger"
        type="button"
        className="internal-nav-trigger"
        aria-label="Mở menu / Open navigation"
        aria-expanded={mobileNavOpen}
        aria-controls="mobile-internal-navigation"
        onClick={onOpenNavigation}
      >
        <span aria-hidden="true">☰</span>
      </button>
      <div className="topbar-title">
        {typeof title === "string" ? <h1>{title}</h1> : title}
      </div>
      <div className="topbar-utility">
        <div className="language-switcher" role="group" aria-label="Chọn ngôn ngữ / Choose language">
          <button type="button" className="lang-btn active" aria-pressed="true" aria-label="Tiếng Việt (Đang chọn / Selected)">VI</button>
          <span className="lang-divider" aria-hidden="true">|</span>
          <button type="button" className="lang-btn" aria-pressed="false" aria-label="English">EN</button>
        </div>
      </div>
    </header>
  );
}
''')

sidebar = (SRC / "components/shell/Sidebar.tsx").read_text(encoding="utf-8")
sidebar = sidebar.replace("const DEFAULT_NAV_ITEMS: NavItem[] = [", "export const DEFAULT_NAV_ITEMS: NavItem[] = [", 1)
write(SRC / "components/shell/Sidebar.tsx", sidebar)

write(SRC / "app/layout.tsx", r'''
import type { Metadata } from "next";
import { headers } from "next/headers";
import { AppShell } from "@/components/shell/AppShell";
import { CandidateShell } from "@/components/shell/CandidateShell";
import "./globals.css";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Tuyển dụng EIU / EIU Recruitment",
  description: "Hệ thống Tuyển dụng Giảng viên & Nhân viên Đại học Quốc tế Miền Đông",
};

type ShellKind = "auth" | "candidate" | "internal";

export function resolveShellKind(pathname: string): ShellKind {
  if (pathname === "/login" || pathname.startsWith("/login/") || pathname.startsWith("/auth/")) {
    return "auth";
  }
  if (pathname === "/candidate" || pathname.startsWith("/candidate/")) {
    return "candidate";
  }
  return "internal";
}

export default async function RootLayout({ children }: LayoutProps<"/">) {
  const reqHeaders = await headers();
  const nonce = reqHeaders.get("x-nonce") ?? undefined;
  const pathname = reqHeaders.get("x-pathname") ?? "";
  const shellKind = resolveShellKind(pathname);

  const content =
    shellKind === "auth" ? children : shellKind === "candidate" ? (
      <CandidateShell>{children}</CandidateShell>
    ) : (
      <AppShell currentPath={pathname}>{children}</AppShell>
    );

  return (
    <html lang="vi">
      <body nonce={nonce}>
        <div id="app-root">{content}</div>
      </body>
    </html>
  );
}
''')

css_path = SRC / "app/globals.css"
css = css_path.read_text(encoding="utf-8")
css += r'''

/* DS-002: responsive Internal shell and explicit Candidate shell */
.internal-nav-trigger {
  display: none;
  inline-size: 44px;
  block-size: 44px;
  border: 1px solid var(--line);
  border-radius: var(--radius-control);
  background: var(--surface);
  color: var(--eiu-blue);
  font-size: 20px;
  place-items: center;
  cursor: pointer;
}
.candidate-shell { min-height: 100vh; background: var(--canvas); }
.candidate-shell__main { min-height: 100vh; outline: none; }
.mobile-nav-layer { position: fixed; inset: 0; z-index: 1000; display: none; }
.mobile-nav-backdrop { position: absolute; inset: 0; border: 0; background: rgba(48,48,51,.52); cursor: pointer; }
.mobile-nav-panel { position: absolute; inset: 0 auto 0 0; inline-size: min(360px, 88vw); display: flex; flex-direction: column; background: linear-gradient(180deg,var(--sidebar-bg-top),var(--sidebar-bg-bottom)); color: var(--sidebar-text); box-shadow: 8px 0 24px rgba(48,48,51,.22); outline: none; }
.mobile-nav-header { min-block-size: 72px; padding: 12px 16px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--sidebar-border); }
.mobile-nav-close { inline-size: 44px; block-size: 44px; border: 1px solid var(--sidebar-border); border-radius: var(--radius-control); background: transparent; color: var(--sidebar-text); font-size: 24px; cursor: pointer; }
.mobile-nav-list { list-style: none; margin: 0; padding: 16px 12px; display: grid; gap: 4px; }
.mobile-nav-list a { min-block-size: 48px; display: flex; align-items: center; padding: 10px 16px; border-radius: var(--radius-control); color: var(--sidebar-text); text-decoration: none; font-size: 16px; font-weight: 500; }
.mobile-nav-list a[aria-current="page"] { background: var(--sidebar-active-bg); color: var(--sidebar-active-text); font-weight: 600; }
.mobile-nav-user { margin-top: auto; padding: 16px; display: grid; gap: 4px; border-top: 1px solid var(--sidebar-border); }
.mobile-nav-user span { color: var(--sidebar-muted); font-size: 14px; }
.sr-only { position: absolute; inline-size: 1px; block-size: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; border: 0; }

@media (max-width: 1024px) {
  .sidebar { display: none; }
  .shell-main { margin-left: 0; }
  .internal-nav-trigger { display: grid; flex: 0 0 auto; }
  .topbar { gap: 12px; padding-inline: 16px; }
  .topbar-title { flex: 1; min-width: 0; }
  .topbar-title h1 { font-size: 24px; }
  .mobile-nav-layer { display: block; }
}
@media (max-width: 430px) {
  .topbar { min-height: 72px; height: auto; padding-block: 10px; }
  .topbar-title h1 { font-size: 20px; }
  .content { padding: 16px; }
}
'''
write(css_path, css)

write(SRC / "__tests__/design-shell.test.ts", r'''
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";

const read = (path: string) => readFileSync(new URL(path, import.meta.url), "utf8");
const layout = read("../app/layout.tsx");
const shell = read("../components/shell/AppShell.tsx");
const mobile = read("../components/shell/MobileNavigation.tsx");
const css = read("../app/globals.css");

test("candidate and internal shell responsibilities are explicit", () => {
  assert.match(layout, /resolveShellKind/);
  assert.match(layout, /CandidateShell/);
  assert.match(layout, /pathname === "\\/candidate"/);
  assert.match(layout, /AppShell currentPath=\{pathname\}/);
});

test("internal mobile navigation is modal, inert and focus restoring", () => {
  assert.match(shell, /MobileNavigation/);
  assert.match(mobile, /createPortal/);
  assert.match(mobile, /aria-modal="true"/);
  assert.match(mobile, /setAttribute\("inert"/);
  assert.match(mobile, /event\.key === "Escape"/);
  assert.match(mobile, /internal-nav-trigger/);
  assert.match(css, /@media \(max-width: 1024px\)/);
  assert.match(css, /\.shell-main \{ margin-left: 0; \}/);
});
''')

run("node", "--conditions", "react-server", "--test", "--import", "tsx", "src/__tests__/design-shell.test.ts", cwd=WEB)
run("npx", "biome", "check", "src/app/layout.tsx", "src/app/globals.css", "src/components/shell/AppShell.tsx", "src/components/shell/CandidateShell.tsx", "src/components/shell/Header.tsx", "src/components/shell/MobileNavigation.tsx", "src/components/shell/Sidebar.tsx", "src/__tests__/design-shell.test.ts", cwd=WEB)
run("npm", "run", "typecheck", cwd=WEB)
run("git", "diff", "--check")
run("git", "add", "web/src/app", "web/src/components/shell", "web/src/__tests__/design-shell.test.ts")
run("git", "commit", "-m", "feat(ds): harden shell architecture and responsive navigation")

# ============================================================================
# DS-003 — bounded reusable primitive layer
# ============================================================================
write(SRC / "components/ui/Button.tsx", r'''
import type { ButtonHTMLAttributes, ReactNode } from "react";

type Variant = "primary" | "secondary" | "ghost" | "danger";
export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  pending?: boolean;
  children: ReactNode;
}
export function Button({ variant = "secondary", pending = false, disabled, className = "", children, ...props }: ButtonProps) {
  return (
    <button {...props} disabled={disabled || pending} aria-busy={pending || undefined} className={`ui-button ui-button--${variant} ${className}`.trim()}>
      {children}
    </button>
  );
}
''')

write(SRC / "components/ui/StatusBadge.tsx", r'''
import type { ButtonHTMLAttributes, ReactNode } from "react";

type Tone = "success" | "warning" | "danger" | "info" | "neutral" | "followup";
interface Common { children: ReactNode; tone?: Tone; operationalInterview?: boolean; className?: string; }
type Props = Common & ({ interactive: true; "aria-label": string } & ButtonHTMLAttributes<HTMLButtonElement> | { interactive?: false });
export function StatusBadge(props: Props) {
  const tone = props.tone ?? "neutral";
  const cls = `ui-status-badge ui-status-badge--${tone} ${props.operationalInterview ? "ui-status-badge--interview" : ""} ${props.className ?? ""}`.trim();
  if (props.interactive) {
    const { children, interactive: _interactive, tone: _tone, operationalInterview: _op, className: _className, ...buttonProps } = props;
    return <button type="button" {...buttonProps} className={cls}>{children}</button>;
  }
  return <span className={cls}>{props.children}</span>;
}
''')

write(SRC / "components/ui/StatusMenu.tsx", r'''
"use client";
import { useEffect, useRef, useState } from "react";

export interface StatusMenuOption { value: string; label: string; disabled?: boolean; }
interface StatusMenuProps { label: string; currentValue?: string; options: StatusMenuOption[]; onSelect: (value: string) => void; }
export function StatusMenu({ label, currentValue, options, onSelect }: StatusMenuProps) {
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);
  useEffect(() => {
    if (!open) return;
    const onPointer = (event: PointerEvent) => { if (!rootRef.current?.contains(event.target as Node)) setOpen(false); };
    const onKey = (event: KeyboardEvent) => { if (event.key === "Escape") { setOpen(false); triggerRef.current?.focus(); } };
    document.addEventListener("pointerdown", onPointer);
    document.addEventListener("keydown", onKey);
    return () => { document.removeEventListener("pointerdown", onPointer); document.removeEventListener("keydown", onKey); };
  }, [open]);
  return (
    <div ref={rootRef} className="ui-status-menu">
      <button ref={triggerRef} type="button" className="ui-status-menu__trigger" aria-haspopup="menu" aria-expanded={open} onClick={() => setOpen((value) => !value)}>{label}</button>
      {open ? <div className="ui-status-menu__panel" role="menu">
        {options.map((option) => <button key={option.value} type="button" role="menuitemradio" aria-checked={option.value === currentValue} disabled={option.disabled} onClick={() => { onSelect(option.value); setOpen(false); }}>{option.label}</button>)}
      </div> : null}
    </div>
  );
}
''')

write(SRC / "components/ui/AsyncStatus.tsx", r'''
import type { ReactNode } from "react";
export function AsyncStatus({ children, kind = "info" }: { children: ReactNode; kind?: "info" | "success" | "error" | "warning" }) {
  return <div className={`ui-async-status ui-async-status--${kind}`} role={kind === "error" ? "alert" : "status"} aria-live={kind === "error" ? "assertive" : "polite"}>{children}</div>;
}
''')

write(SRC / "components/ui/TableScrollContainer.tsx", r'''
import type { ReactNode } from "react";
export function TableScrollContainer({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <div className={`ui-table-scroll ${className}`.trim()} tabIndex={0} aria-label="Bảng dữ liệu có thể cuộn ngang / Horizontally scrollable data table">{children}</div>;
}
''')

write(SRC / "components/ui/overlay.tsx", r'''
"use client";
import type { RefObject } from "react";
import { useEffect } from "react";

const FOCUSABLE = 'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';
export function useOverlayFocus(open: boolean, containerRef: RefObject<HTMLElement | null>, onClose: () => void) {
  useEffect(() => {
    if (!open) return;
    const previous = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    const appRoot = document.getElementById("app-root");
    const previousOverflow = document.body.style.overflow;
    appRoot?.setAttribute("inert", "");
    appRoot?.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "hidden";
    const focusable = () => Array.from(containerRef.current?.querySelectorAll<HTMLElement>(FOCUSABLE) ?? []);
    requestAnimationFrame(() => focusable()[0]?.focus());
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") { event.preventDefault(); onClose(); return; }
      if (event.key !== "Tab") return;
      const items = focusable(); if (!items.length) return;
      const first = items[0]; const last = items[items.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    };
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("keydown", onKey);
      appRoot?.removeAttribute("inert"); appRoot?.removeAttribute("aria-hidden");
      document.body.style.overflow = previousOverflow;
      previous?.focus();
    };
  }, [open, containerRef, onClose]);
}
''')

write(SRC / "components/ui/Dialog.tsx", r'''
"use client";
import type { ReactNode } from "react";
import { useRef } from "react";
import { createPortal } from "react-dom";
import { useOverlayFocus } from "./overlay";
export function Dialog({ open, title, children, onClose, footer }: { open: boolean; title: string; children: ReactNode; onClose: () => void; footer?: ReactNode }) {
  const ref = useRef<HTMLDivElement>(null); useOverlayFocus(open, ref, onClose);
  if (!open || typeof document === "undefined") return null;
  return createPortal(<div className="ui-overlay"><button type="button" className="ui-overlay__backdrop" aria-label="Đóng / Close" onClick={onClose}/><div ref={ref} className="ui-dialog" role="dialog" aria-modal="true" aria-label={title}><header><h2>{title}</h2><button type="button" className="ui-icon-button" onClick={onClose} aria-label="Đóng / Close">×</button></header><div className="ui-dialog__body">{children}</div>{footer ? <footer>{footer}</footer> : null}</div></div>, document.body);
}
''')

write(SRC / "components/ui/Drawer.tsx", r'''
"use client";
import type { ReactNode } from "react";
import { useRef } from "react";
import { createPortal } from "react-dom";
import { useOverlayFocus } from "./overlay";
export function Drawer({ open, title, children, onClose, footer }: { open: boolean; title: string; children: ReactNode; onClose: () => void; footer?: ReactNode }) {
  const ref = useRef<HTMLElement>(null); useOverlayFocus(open, ref, onClose);
  if (!open || typeof document === "undefined") return null;
  return createPortal(<div className="ui-overlay ui-overlay--drawer"><button type="button" className="ui-overlay__backdrop" aria-label="Đóng / Close" onClick={onClose}/><aside ref={ref} className="ui-drawer" role="dialog" aria-modal="true" aria-label={title}><header><h2>{title}</h2><button type="button" className="ui-icon-button" onClick={onClose} aria-label="Đóng / Close">×</button></header><div className="ui-drawer__body">{children}</div>{footer ? <footer>{footer}</footer> : null}</aside></div>, document.body);
}
''')

write(SRC / "styles/ui.css", r'''
.ui-button { min-height: 44px; min-width: 44px; display: inline-flex; align-items: center; justify-content: center; gap: 8px; padding: 0 16px; border-radius: var(--radius-control); border: 1px solid transparent; font: inherit; font-size: 16px; font-weight: 600; cursor: pointer; }
.ui-button:disabled { opacity: .58; cursor: not-allowed; }
.ui-button--primary { background: var(--eiu-blue); color: var(--surface); }
.ui-button--secondary { background: var(--surface); color: var(--eiu-blue); border-color: var(--eiu-blue); }
.ui-button--ghost { background: transparent; color: var(--eiu-blue); border-color: var(--line); }
.ui-button--danger { background: var(--status-danger-bg); color: var(--status-danger-text); border-color: var(--status-danger-text); }
.ui-icon-button { inline-size: 44px; block-size: 44px; display: grid; place-items: center; border: 1px solid var(--line); border-radius: var(--radius-control); background: var(--surface); color: var(--ink-950); font-size: 20px; cursor: pointer; }
.ui-status-badge { min-height: var(--badge-min-height); display: inline-flex; align-items: center; justify-content: center; padding: 4px 10px; border: 0; border-radius: var(--radius-badge); font-size: 16px; font-weight: 600; line-height: 1.25; text-align: center; white-space: normal; }
.ui-status-badge--interview { width: var(--badge-width-interview-operational); }
.ui-status-badge--success { color: var(--status-success-text); background: var(--status-success-bg); }
.ui-status-badge--warning { color: var(--status-warning-text); background: var(--status-warning-bg); }
.ui-status-badge--danger { color: var(--status-danger-text); background: var(--status-danger-bg); }
.ui-status-badge--info { color: var(--status-info-text); background: var(--status-info-bg); }
.ui-status-badge--neutral { color: var(--status-neutral-text); background: var(--status-neutral-bg); }
.ui-status-badge--followup { color: var(--status-followup-text); background: var(--status-followup-bg); }
.ui-status-menu { position: relative; display: inline-flex; }
.ui-status-menu__trigger { min-height: 44px; padding: 0 14px; border: 1px solid var(--line); border-radius: var(--radius-control); background: var(--surface); color: var(--ink-950); font-size: 16px; cursor: pointer; }
.ui-status-menu__panel { position: absolute; z-index: 60; inset: calc(100% + 6px) auto auto 0; width: min(280px, calc(100vw - 32px)); display: grid; padding: 6px; background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius-control); box-shadow: 0 12px 30px rgba(48,48,51,.18); }
.ui-status-menu__panel button { min-height: 44px; border: 0; border-radius: 8px; background: transparent; color: var(--ink-950); font-size: 16px; text-align: left; padding: 8px 12px; cursor: pointer; }
.ui-status-menu__panel button[aria-checked="true"] { background: var(--eiu-cream); font-weight: 600; }
.ui-async-status { padding: 12px 16px; border: 1px solid var(--line); border-radius: var(--radius-control); background: var(--surface); color: var(--ink-950); font-size: 16px; }
.ui-async-status--error { background: var(--status-danger-bg); color: var(--status-danger-text); border-color: var(--status-danger-text); }
.ui-async-status--warning { background: var(--status-warning-bg); color: var(--status-warning-text); border-color: var(--status-warning-text); }
.ui-async-status--success { background: var(--status-success-bg); color: var(--status-success-text); border-color: var(--status-success-text); }
.ui-table-scroll { overflow: auto; overscroll-behavior-inline: contain; border: 1px solid var(--line); border-radius: var(--radius-card); background: var(--surface); box-shadow: inset -12px 0 12px -16px var(--ink-950); }
.ui-overlay { position: fixed; inset: 0; z-index: 1100; display: grid; place-items: center; padding: 16px; }
.ui-overlay--drawer { place-items: stretch end; padding: 0; }
.ui-overlay__backdrop { position: absolute; inset: 0; border: 0; background: rgba(48,48,51,.52); cursor: pointer; }
.ui-dialog, .ui-drawer { position: relative; z-index: 1; background: var(--surface); color: var(--ink-950); box-shadow: 0 18px 48px rgba(48,48,51,.24); outline: none; }
.ui-dialog { width: min(760px, calc(100vw - 32px)); max-height: min(88dvh, 900px); border-radius: var(--radius-overlay); overflow: hidden; }
.ui-drawer { width: min(820px, calc(100vw - 32px)); height: 100dvh; display: flex; flex-direction: column; }
.ui-dialog > header, .ui-drawer > header { min-height: 64px; position: sticky; top: 0; display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 12px 20px; border-bottom: 1px solid var(--line); background: var(--surface); }
.ui-dialog h2, .ui-drawer h2 { margin: 0; font-size: 22px; color: var(--eiu-blue); }
.ui-dialog__body, .ui-drawer__body { padding: 24px; overflow: auto; font-size: 16px; }
.ui-dialog > footer, .ui-drawer > footer { position: sticky; bottom: 0; padding: 12px 20px; border-top: 1px solid var(--line); background: var(--surface); }
@media (max-width: 767px) { .ui-overlay--drawer { padding: 0; } .ui-drawer { width: 100vw; height: 100dvh; } .ui-dialog { width: calc(100vw - 24px); } .ui-dialog__body, .ui-drawer__body { padding: 16px; } }
''')

css_path = SRC / "app/globals.css"
css = css_path.read_text(encoding="utf-8")
if '@import "../styles/ui.css";' not in css:
    css = css.replace('@import "../styles/login.css";\n', '@import "../styles/login.css";\n@import "../styles/ui.css";\n', 1)
write(css_path, css)

write(SRC / "__tests__/design-primitives.test.ts", r'''
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
const read = (path: string) => readFileSync(new URL(path, import.meta.url), "utf8");
test("bounded production primitives expose current design contracts", () => {
  assert.match(read("../components/ui/Button.tsx"), /pending/);
  assert.match(read("../components/ui/StatusBadge.tsx"), /operationalInterview/);
  const menu = read("../components/ui/StatusMenu.tsx");
  assert.match(menu, /aria-haspopup="menu"/); assert.match(menu, /Escape/); assert.match(menu, /rootRef/);
  const overlay = read("../components/ui/overlay.tsx");
  assert.match(overlay, /setAttribute\("inert"/); assert.match(overlay, /previous\?\.focus/);
  const css = read("../styles/ui.css");
  assert.match(css, /--badge-width-interview-operational/); assert.match(css, /width: min\(820px/);
});
''')

run("node", "--conditions", "react-server", "--test", "--import", "tsx", "src/__tests__/design-primitives.test.ts", cwd=WEB)
run("npx", "biome", "check", "src/components/ui", "src/styles/ui.css", "src/app/globals.css", "src/__tests__/design-primitives.test.ts", cwd=WEB)
run("npm", "run", "typecheck", cwd=WEB)
run("git", "diff", "--check")
run("git", "add", "web/src/components/ui", "web/src/styles/ui.css", "web/src/app/globals.css", "web/src/__tests__/design-primitives.test.ts")
run("git", "commit", "-m", "feat(ds): add bounded reusable UI primitives")
run("git", "push", "origin", "HEAD:oanhpham-kobe/DESIGN-SYSTEM-HARDENING-001")
