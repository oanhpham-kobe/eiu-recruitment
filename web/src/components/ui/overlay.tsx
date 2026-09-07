"use client";
import type { RefObject } from "react";
import { useEffect } from "react";

const FOCUSABLE =
  'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';

let activeOverlayLocks = 0;
let originalBodyOverflow: string | null = null;

function acquireBackgroundLock() {
  if (activeOverlayLocks === 0) {
    const appRoot = document.getElementById("app-root");
    originalBodyOverflow = document.body.style.overflow;
    appRoot?.setAttribute("inert", "");
    appRoot?.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "hidden";
  }
  activeOverlayLocks += 1;
}

function releaseBackgroundLock() {
  activeOverlayLocks = Math.max(0, activeOverlayLocks - 1);
  if (activeOverlayLocks !== 0) return;

  const appRoot = document.getElementById("app-root");
  appRoot?.removeAttribute("inert");
  appRoot?.removeAttribute("aria-hidden");
  document.body.style.overflow = originalBodyOverflow ?? "";
  originalBodyOverflow = null;
}

export function useOverlayFocus(
  open: boolean,
  containerRef: RefObject<HTMLElement | null>,
  onClose: () => void,
) {
  useEffect(() => {
    if (!open) return;
    const previous =
      document.activeElement instanceof HTMLElement
        ? document.activeElement
        : null;

    acquireBackgroundLock();

    const focusable = () =>
      Array.from(
        containerRef.current?.querySelectorAll<HTMLElement>(FOCUSABLE) ?? [],
      );
    requestAnimationFrame(() => focusable()[0]?.focus());

    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.preventDefault();
        onClose();
        return;
      }
      if (event.key !== "Tab") return;
      const items = focusable();
      if (!items.length) return;
      const first = items[0];
      const last = items[items.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    };

    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("keydown", onKey);
      releaseBackgroundLock();
      previous?.focus();
    };
  }, [open, containerRef, onClose]);
}
