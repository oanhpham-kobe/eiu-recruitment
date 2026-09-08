"use client";

import { useAppLocale } from "./LocaleProvider";

export interface NavItem {
  href: string;
  labelVi: string;
  labelEn: string;
}

export const DEFAULT_NAV_ITEMS: NavItem[] = [
  { href: "/", labelVi: "Tổng quan", labelEn: "Overview" },
  {
    href: "#applications",
    labelVi: "Hồ sơ ứng tuyển",
    labelEn: "Applications",
  },
  { href: "/interviews", labelVi: "Lịch phỏng vấn", labelEn: "Interviews" },
  { href: "/reports", labelVi: "Báo cáo phỏng vấn", labelEn: "Interview Reports" },
];

export interface SidebarProps {
  currentPath?: string;
  navItems?: NavItem[];
}

export function Sidebar({
  currentPath = "/",
  navItems = DEFAULT_NAV_ITEMS,
}: SidebarProps) {
  const { locale } = useAppLocale();

  return (
    <aside
      className="sidebar"
      aria-label={locale === "vi" ? "Thanh điều hướng chính" : "Main sidebar"}
    >
      <div className="sidebar-brand">
        <div className="brand-logo">
          <span className="brand-text">EIU</span>
          <span className="brand-mark" aria-hidden="true">
            <i />
            <i />
            <i />
          </span>
        </div>
        <div className="brand-sub">
          {locale === "vi" ? "Tuyển dụng" : "Recruitment"}
        </div>
      </div>

      <nav
        className="sidebar-nav"
        aria-label={locale === "vi" ? "Menu chức năng" : "Navigation menu"}
      >
        <ul className="nav-list">
          {navItems.map((item) => {
            const isCurrent = currentPath === item.href;
            return (
              <li key={item.href} className="nav-item">
                <a
                  href={item.href}
                  aria-current={isCurrent ? "page" : undefined}
                >
                  {locale === "vi" ? item.labelVi : item.labelEn}
                </a>
              </li>
            );
          })}
        </ul>
      </nav>

      <div className="sidebar-user">
        <div
          className="user-avatar"
          role="img"
          aria-label={locale === "vi" ? "Ảnh đại diện người dùng" : "User avatar"}
        >
          IU
        </div>
        <div className="user-info">
          <span className="user-name">
            {locale === "vi" ? "Người dùng nội bộ" : "Internal User"}
          </span>
          <span className="user-role">
            EIU Recruitment
          </span>
        </div>
      </div>
    </aside>
  );
}
