import type { Metadata } from "next";
import { headers } from "next/headers";
import { AppShell } from "@/components/shell/AppShell";
import { CandidateShell } from "@/components/shell/CandidateShell";
import { getServerSession } from "@/lib/auth/session";
import { createServerClient } from "@/lib/supabase/server";
import "./globals.css";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Tuyển dụng EIU / EIU Recruitment",
  description:
    "Hệ thống Tuyển dụng Giảng viên & Nhân viên Đại học Quốc tế Miền Đông",
};

type ShellKind = "auth" | "candidate" | "internal";

export function resolveShellKind(pathname: string): ShellKind {
  if (
    pathname === "/login" ||
    pathname.startsWith("/login/") ||
    pathname.startsWith("/auth/")
  ) {
    return "auth";
  }
  if (pathname === "/candidate" || pathname.startsWith("/candidate/")) {
    return "candidate";
  }
  return "internal";
}

export default async function RootLayout({ children }: LayoutProps<"/">) {
  const reqHeaders = await headers();
  const nonce = reqHeaders.get("x-nonce") ?? undefined;
  const pathname = reqHeaders.get("x-pathname") ?? "";
  const shellKind = resolveShellKind(pathname);
  let showInterviews = false;
  if (shellKind === "internal") {
    const session = await getServerSession(await createServerClient());
    showInterviews = Boolean(
      session.user?.roles.includes("ROOT_ADMIN") ||
        session.user?.permissions.includes("interviews.view"),
    );
  }

  const content =
    shellKind === "auth" ? (
      children
    ) : shellKind === "candidate" ? (
      <CandidateShell>{children}</CandidateShell>
    ) : (
      <AppShell currentPath={pathname} showInterviews={showInterviews}>
        {children}
      </AppShell>
    );

  return (
    <html lang="vi">
      <body nonce={nonce}>
        <div id="app-root">{content}</div>
      </body>
    </html>
  );
}
