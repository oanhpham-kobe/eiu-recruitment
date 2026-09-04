import type React from "react";

export interface HeaderProps {
  title?: React.ReactNode;
}

export function Header({
  title = "Hệ thống Tuyển dụng EIU / EIU Recruitment",
}: HeaderProps) {
  return (
    <header className="topbar">
      <div className="topbar-title">
        {typeof title === "string" ? <h1>{title}</h1> : title}
      </div>

      <div className="topbar-utility">
        {/* biome-ignore lint/a11y/useSemanticElements: toolbar button group per WAI-ARIA pattern */}
        <div
          className="language-switcher"
          role="group"
          aria-label="Chọn ngôn ngữ / Choose language"
        >
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
        </div>
      </div>
    </header>
  );
}
