"use client";

import { useEffect, useRef, useState } from "react";

export type AutosaveStatus = "IDLE" | "SAVING" | "SAVED" | "RESTORED";

interface UseAutosaveOptions<T> {
  sessionId: string;
  data: T;
  debounceMs?: number;
  onRestore?: (restoredData: T) => void;
}

export function useAutosave<T>({
  sessionId,
  data,
  debounceMs = 800,
  onRestore,
}: UseAutosaveOptions<T>) {
  const [status, setStatus] = useState<AutosaveStatus>("IDLE");
  const [lastSavedAt, setLastSavedAt] = useState<Date | null>(null);
  const storageKey = `eiu_candidate_form_draft_${sessionId}`;
  const isInitialMount = useRef(true);
  const onRestoreRef = useRef(onRestore);
  onRestoreRef.current = onRestore;

  // Restore draft on mount
  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }
    try {
      const saved = localStorage.getItem(storageKey);
      if (saved) {
        const parsed = JSON.parse(saved) as T;
        onRestoreRef.current?.(parsed);
        setStatus("RESTORED");
      }
    } catch {
      // Ignore localStorage parse errors
    }
  }, [storageKey]);

  // Debounced save on data change
  useEffect(() => {
    if (isInitialMount.current) {
      isInitialMount.current = false;
      return;
    }

    if (!sessionId || typeof window === "undefined") {
      return;
    }

    setStatus("SAVING");
    const timer = setTimeout(() => {
      try {
        localStorage.setItem(storageKey, JSON.stringify(data));
        setStatus("SAVED");
        setLastSavedAt(new Date());
      } catch {
        setStatus("IDLE");
      }
    }, debounceMs);

    return () => clearTimeout(timer);
  }, [data, sessionId, debounceMs, storageKey]);

  const clearDraft = () => {
    if (typeof window !== "undefined") {
      try {
        localStorage.removeItem(storageKey);
        setStatus("IDLE");
        setLastSavedAt(null);
      } catch {
        // Ignore removal errors
      }
    }
  };

  const getStatusMessage = (): string => {
    switch (status) {
      case "SAVING":
        return "Đang lưu bản nháp... / Saving draft...";
      case "SAVED":
        return "Đã lưu bản nháp tự động / Draft autosaved";
      case "RESTORED":
        return "Đã khôi phục bản nháp đã lưu / Restored saved draft";
      default:
        return "";
    }
  };

  return {
    status,
    lastSavedAt,
    clearDraft,
    statusMessage: getStatusMessage(),
  };
}
