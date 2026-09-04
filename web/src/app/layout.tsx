import type { Metadata } from "next";
import { headers } from "next/headers";
import { AppShell } from "@/components/shell/AppShell";
import "./globals.css";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Tuyển dụng EIU / EIU Recruitment",
  description:
    "Hệ thống Tuyển dụng Giảng viên & Nhân viên Đại học Quốc tế Miền Đông",
};

export default async function RootLayout({ children }: LayoutProps<"/">) {
  const reqHeaders = await headers();
  const nonce = reqHeaders.get("x-nonce") ?? undefined;
  const pathname = reqHeaders.get("x-pathname") ?? "";
  const isAuthRoute = pathname === "/login" || pathname.startsWith("/login");

  return (
    <html lang="vi">
      <body nonce={nonce}>
        {isAuthRoute ? children : <AppShell>{children}</AppShell>}
      </body>
    </html>
  );
}
