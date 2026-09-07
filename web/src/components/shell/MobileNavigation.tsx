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

export function MobileNavigation({
  open,
  currentPath,
  onClose,
}: MobileNavigationProps) {
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
          <button
            ref={closeRef}
            type="button"
            className="mobile-nav-close"
            onClick={onClose}
          >
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
