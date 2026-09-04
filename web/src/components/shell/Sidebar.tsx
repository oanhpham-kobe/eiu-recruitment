interface NavItem {
  href: string;
  label: string;
}

const DEFAULT_NAV_ITEMS: NavItem[] = [
  { href: "/", label: "Tổng quan / Overview" },
  { href: "#applications", label: "Hồ sơ ứng tuyển / Applications" },
  { href: "#interviews", label: "Lịch phỏng vấn / Interviews" },
  { href: "#reports", label: "Báo cáo / Reports" },
];

export interface SidebarProps {
  currentPath?: string;
  navItems?: NavItem[];
}

export function Sidebar({
  currentPath = "/",
  navItems = DEFAULT_NAV_ITEMS,
}: SidebarProps) {
  return (
    <aside
      className="sidebar"
      aria-label="Thanh điều hướng chính / Main sidebar"
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
        <div className="brand-sub">Tuyển dụng / Recruitment</div>
      </div>

      <nav
        className="sidebar-nav"
        aria-label="Menu chức năng / Navigation menu"
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
                  {item.label}
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
          aria-label="Ảnh đại diện người dùng / User avatar"
        >
          HR
        </div>
        <div className="user-info">
          <span className="user-name">Quản trị viên / Admin</span>
          <span className="user-role">Phòng Nhân sự / HR Department</span>
        </div>
      </div>
    </aside>
  );
}
