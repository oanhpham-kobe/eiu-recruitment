from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    file = Path(path)
    text = file.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: expected one match, found {count}: {old[:120]!r}")
    file.write_text(text.replace(old, new, 1), encoding="utf-8")


path = "web/src/components/ui/StatusMenu.tsx"
replace_once(
    path,
    '''  const openFocusRef = useRef<OpenFocus>("current");

  const enabledItems = useCallback(
''',
    '''  const openFocusRef = useRef<OpenFocus>("current");

  const positionPanel = useCallback(() => {
    const panel = panelRef.current;
    const root = rootRef.current;
    const trigger = triggerRef.current;
    if (!panel || !root || !trigger) return;

    panel.style.left = "0px";
    const rootRect = root.getBoundingClientRect();
    const triggerRect = trigger.getBoundingClientRect();
    const panelWidth = panel.getBoundingClientRect().width;
    const gutter = 16;
    const maxViewportLeft = Math.max(
      gutter,
      window.innerWidth - panelWidth - gutter,
    );
    const viewportLeft = Math.min(
      Math.max(triggerRect.left, gutter),
      maxViewportLeft,
    );
    panel.style.left = `${viewportLeft - rootRect.left}px`;
  }, []);

  const enabledItems = useCallback(
''',
)
replace_once(
    path,
    '''    const focusMenu = requestAnimationFrame(() => {
      const items = enabledItems();
''',
    '''    const focusMenu = requestAnimationFrame(() => {
      positionPanel();
      const items = enabledItems();
''',
)
replace_once(
    path,
    '''    document.addEventListener("pointerdown", onPointer);
    document.addEventListener("keydown", onKey);
    return () => {
      cancelAnimationFrame(focusMenu);
      document.removeEventListener("pointerdown", onPointer);
      document.removeEventListener("keydown", onKey);
    };
  }, [enabledItems, open]);
''',
    '''    document.addEventListener("pointerdown", onPointer);
    document.addEventListener("keydown", onKey);
    window.addEventListener("resize", positionPanel);
    return () => {
      cancelAnimationFrame(focusMenu);
      document.removeEventListener("pointerdown", onPointer);
      document.removeEventListener("keydown", onKey);
      window.removeEventListener("resize", positionPanel);
    };
  }, [enabledItems, open, positionPanel]);
''',
)
