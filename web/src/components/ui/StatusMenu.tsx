"use client";
import {
  type KeyboardEvent as ReactKeyboardEvent,
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";

export interface StatusMenuOption {
  value: string;
  label: string;
  disabled?: boolean;
}

interface StatusMenuProps {
  label: string;
  currentValue?: string;
  options: StatusMenuOption[];
  onSelect: (value: string) => void;
}

type OpenFocus = "current" | "first" | "last";

export function StatusMenu({
  label,
  currentValue,
  options,
  onSelect,
}: StatusMenuProps) {
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);
  const panelRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const openFocusRef = useRef<OpenFocus>("current");

  const enabledItems = useCallback(
    () =>
      Array.from(
        panelRef.current?.querySelectorAll<HTMLButtonElement>(
          '[role="menuitemradio"]:not(:disabled)',
        ) ?? [],
      ),
    [],
  );

  useEffect(() => {
    if (!open) return;

    const focusMenu = requestAnimationFrame(() => {
      const items = enabledItems();
      if (items.length === 0) return;
      if (openFocusRef.current === "first") {
        items[0].focus();
        return;
      }
      if (openFocusRef.current === "last") {
        items[items.length - 1].focus();
        return;
      }
      const current = items.find(
        (item) => item.getAttribute("aria-checked") === "true",
      );
      (current ?? items[0]).focus();
    });

    const onPointer = (event: PointerEvent) => {
      if (!rootRef.current?.contains(event.target as Node)) setOpen(false);
    };
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.preventDefault();
        setOpen(false);
        triggerRef.current?.focus();
      }
    };

    document.addEventListener("pointerdown", onPointer);
    document.addEventListener("keydown", onKey);
    return () => {
      cancelAnimationFrame(focusMenu);
      document.removeEventListener("pointerdown", onPointer);
      document.removeEventListener("keydown", onKey);
    };
  }, [enabledItems, open]);

  const openMenu = (focus: OpenFocus) => {
    openFocusRef.current = focus;
    setOpen(true);
  };

  const moveMenuFocus = (event: ReactKeyboardEvent<HTMLDivElement>) => {
    const items = enabledItems();
    if (items.length === 0) return;
    const currentIndex = items.indexOf(
      document.activeElement as HTMLButtonElement,
    );
    let nextIndex: number | undefined;

    if (event.key === "ArrowDown") {
      nextIndex = currentIndex < 0 ? 0 : (currentIndex + 1) % items.length;
    } else if (event.key === "ArrowUp") {
      nextIndex =
        currentIndex < 0
          ? items.length - 1
          : (currentIndex - 1 + items.length) % items.length;
    } else if (event.key === "Home") {
      nextIndex = 0;
    } else if (event.key === "End") {
      nextIndex = items.length - 1;
    } else if (event.key === "Tab") {
      setOpen(false);
      return;
    }

    if (nextIndex !== undefined) {
      event.preventDefault();
      items[nextIndex].focus();
    }
  };

  return (
    <div ref={rootRef} className="ui-status-menu">
      <button
        ref={triggerRef}
        type="button"
        className="ui-status-menu__trigger"
        aria-haspopup="menu"
        aria-expanded={open}
        onClick={() => {
          if (open) {
            setOpen(false);
          } else {
            openMenu("current");
          }
        }}
        onKeyDown={(event) => {
          if (event.key === "ArrowDown") {
            event.preventDefault();
            openMenu("first");
          } else if (event.key === "ArrowUp") {
            event.preventDefault();
            openMenu("last");
          }
        }}
      >
        {label}
      </button>
      {open ? (
        <div
          ref={panelRef}
          className="ui-status-menu__panel"
          role="menu"
          onKeyDown={moveMenuFocus}
        >
          {options.map((option) => (
            <button
              key={option.value}
              type="button"
              role="menuitemradio"
              aria-checked={option.value === currentValue}
              disabled={option.disabled}
              onClick={() => {
                onSelect(option.value);
                setOpen(false);
                triggerRef.current?.focus();
              }}
            >
              {option.label}
            </button>
          ))}
        </div>
      ) : null}
    </div>
  );
}
