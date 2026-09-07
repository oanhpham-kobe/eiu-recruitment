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
        <fieldset className="language-switcher">
          <legend className="sr-only">Chọn ngôn ngữ / Choose language</legend>
          <button
            type="button"
            className="lang-btn active"
            aria-pressed="true"
            aria-label="Tiếng Việt (Đang chọn / Selected)"
          >
            VI
          </button>
          <span className="lang-divider" aria-hidden="true">
            |
          </span>
          <button
            type="button"
            className="lang-btn"
            aria-pressed="false"
            aria-label="English"
          >
            EN
          </button>
        </fieldset>
      </div>
    </header>
  );
}
