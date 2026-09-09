"use client";

import { useAppLocale } from "./LocaleProvider";
import type { NavItem } from "./navigation";

export interface SidebarProps {
  currentPath?: string;
  navItems: readonly NavItem[];
}

export function Sidebar({ currentPath = "/", navItems }: SidebarProps) {
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
          aria-label={
            locale === "vi" ? "Ảnh đại diện người dùng" : "User avatar"
          }
        >
          IU
        </div>
        <div className="user-info">
          <span className="user-name">
            {locale === "vi" ? "Người dùng nội bộ" : "Internal User"}
          </span>
          <span className="user-role">EIU Recruitment</span>
        </div>
      </div>
    </aside>
  );
}
