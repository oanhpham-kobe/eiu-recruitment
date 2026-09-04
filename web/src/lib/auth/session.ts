import "server-only";

import type { SupabaseClient } from "@supabase/supabase-js";
import { createServerClient } from "@/lib/supabase/server";

export interface AppUserSession {
  authUserId: string;
  email: string;
  isInternal: boolean;
  isCandidate: boolean;
  appUserId?: string;
  candidateId?: string;
  roles: string[];
  permissions: string[];
}

export interface AppSession {
  user: AppUserSession | null;
  isAuthenticated: boolean;
}

function extractRoles(appUser: unknown): string[] {
  if (
    appUser &&
    typeof appUser === "object" &&
    "app_user_roles" in appUser &&
    Array.isArray(appUser.app_user_roles)
  ) {
    const roles: string[] = [];
    for (const item of appUser.app_user_roles) {
      if (
        item &&
        typeof item === "object" &&
        "role_code" in item &&
        typeof item.role_code === "string"
      ) {
        roles.push(item.role_code);
      }
    }
    return roles;
  }
  return [];
}

function extractPermissions(appUser: unknown): string[] {
  if (
    appUser &&
    typeof appUser === "object" &&
    "app_user_permissions" in appUser &&
    Array.isArray(appUser.app_user_permissions)
  ) {
    const permissions: string[] = [];
    for (const item of appUser.app_user_permissions) {
      if (
        item &&
        typeof item === "object" &&
        "permission_code" in item &&
        typeof item.permission_code === "string"
      ) {
        permissions.push(item.permission_code);
      }
    }
    return permissions;
  }
  return [];
}

export async function getServerSession(
  client?: SupabaseClient,
): Promise<AppSession> {
  const supabase = client ?? (await createServerClient());
  const {
    data: { user },
    error,
  } = await supabase.auth.getUser();

  if (error || !user || !user.email) {
    return { user: null, isAuthenticated: false };
  }

  const isInternal = user.email.toLowerCase().endsWith("@eiu.edu.vn");

  if (isInternal) {
    const { data: appUser } = await supabase
      .from("app_users")
      .select(
        "app_user_id, is_active, is_root_admin, app_user_roles(role_code), app_user_permissions(permission_code)",
      )
      .eq("auth_user_id", user.id)
      .single();

    if (
      !appUser ||
      typeof appUser !== "object" ||
      !("is_active" in appUser) ||
      !appUser.is_active ||
      !("app_user_id" in appUser) ||
      typeof appUser.app_user_id !== "string"
    ) {
      return { user: null, isAuthenticated: false };
    }

    const roles = extractRoles(appUser);
    const permissions = extractPermissions(appUser);

    return {
      isAuthenticated: true,
      user: {
        authUserId: user.id,
        email: user.email,
        isInternal: true,
        isCandidate: false,
        appUserId: appUser.app_user_id,
        roles,
        permissions,
      },
    };
  }

  const { data: candidate } = await supabase
    .from("candidates")
    .select("candidate_id, is_active")
    .eq("auth_user_id", user.id)
    .single();

  if (
    !candidate ||
    typeof candidate !== "object" ||
    !("is_active" in candidate) ||
    !candidate.is_active ||
    !("candidate_id" in candidate) ||
    typeof candidate.candidate_id !== "string"
  ) {
    return { user: null, isAuthenticated: false };
  }

  return {
    isAuthenticated: true,
    user: {
      authUserId: user.id,
      email: user.email,
      isInternal: false,
      isCandidate: true,
      candidateId: candidate.candidate_id,
      roles: ["CANDIDATE"],
      permissions: ["candidate.self"],
    },
  };
}
