import type { SupabaseClient } from "@supabase/supabase-js";
import { type NextRequest, NextResponse } from "next/server";
import { provisionInternalUserIdentity } from "@/lib/auth/internal";
import { createServerClient } from "@/lib/supabase/server";

export const dynamic = "force-dynamic";

export async function GET(
  request: NextRequest,
  _context?: unknown,
  clientOverride?: SupabaseClient,
) {
  const requestUrl = new URL(request.url);
  const code = requestUrl.searchParams.get("code");
  const rawNext = requestUrl.searchParams.get("next") || "/";

  // Open redirect defense: reject external protocols, protocol-relative, and backslash bypasses
  const next =
    rawNext.startsWith("/") &&
    !rawNext.startsWith("//") &&
    !rawNext.startsWith("/\\")
      ? rawNext
      : "/";

  if (!code) {
    return NextResponse.redirect(
      new URL("/login?error=MISSING_CODE", request.url),
    );
  }

  const supabase = clientOverride ?? (await createServerClient());
  const { error: exchangeError } =
    await supabase.auth.exchangeCodeForSession(code);
  if (exchangeError) {
    return NextResponse.redirect(
      new URL("/login?error=AUTH_EXCHANGE_FAILED", request.url),
    );
  }

  // Provision internal identity
  const provisionResult = await provisionInternalUserIdentity(supabase);
  if (!provisionResult.success) {
    await supabase.auth.signOut();
    const errCode = provisionResult.error.code;
    return NextResponse.redirect(
      new URL(`/login?error=${encodeURIComponent(errCode)}`, request.url),
    );
  }

  return NextResponse.redirect(new URL(next, request.url));
}
