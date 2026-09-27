"use server";

import { getServerSession } from "@/lib/auth/session";
import {
  type AssignHrRoleData,
  assignHrRole,
  type CreateInternalUserData,
  createInternalUser,
  type GrantHrPermissionData,
  grantHrPermission,
  type RevokeHrPermissionData,
  type RevokeHrRoleData,
  revokeHrPermission,
  revokeHrRole,
  type SetInternalUserActiveData,
  setInternalUserActive,
  type UpdateInternalUserDirectoryData,
  type UserCommandDeps,
  updateInternalUserDirectory,
} from "@/lib/commands/internal-users";
import { createServerClient } from "@/lib/supabase/server";

export interface InternalUserDirectoryRecord {
  appUserId: string;
  email: string;
  fullName: string;
  jobTitle: string | null;
  unitId: string | null;
  isActive: boolean;
  isRootAdmin: boolean;
  isHr: boolean;
  identityBound: boolean;
  versionNo: number;
}

export interface PermissionDefinition {
  code: string;
  labelVi: string;
  labelEn: string;
  category: string;
}

export const DELEGABLE_PERMISSIONS: readonly PermissionDefinition[] = [
  // Hồ sơ ứng tuyển
  {
    code: "submissions.view",
    labelVi: "Xem danh sách và chi tiết hồ sơ",
    labelEn: "View Submissions",
    category: "Hồ sơ (Submissions)",
  },
  {
    code: "submissions.edit",
    labelVi: "Chỉnh sửa thông tin hồ sơ",
    labelEn: "Edit Submissions",
    category: "Hồ sơ (Submissions)",
  },
  {
    code: "submissions.status",
    labelVi: "Cập nhật trạng thái thủ công hồ sơ",
    labelEn: "Update Submission Status",
    category: "Hồ sơ (Submissions)",
  },
  // Ứng viên
  {
    code: "candidates.active_manage",
    labelVi: "Khóa / Mở khóa ứng viên",
    labelEn: "Manage Candidate Active Status",
    category: "Ứng viên (Candidates)",
  },
  {
    code: "candidates.delete_unused",
    labelVi: "Xóa ứng viên chưa có hồ sơ",
    labelEn: "Delete Unused Candidates",
    category: "Ứng viên (Candidates)",
  },
  {
    code: "candidates.identity_manage",
    labelVi: "Liên kết lại danh tính ứng viên",
    labelEn: "Manage Candidate Identity",
    category: "Ứng viên (Candidates)",
  },
  // Ứng tuyển
  {
    code: "applications.view",
    labelVi: "Xem hồ sơ phân công tuyển dụng",
    labelEn: "View Applications",
    category: "Ứng tuyển (Applications)",
  },
  {
    code: "applications.manage",
    labelVi: "Tạo và quản lý phân công tuyển dụng",
    labelEn: "Manage Applications",
    category: "Ứng tuyển (Applications)",
  },
  // Phỏng vấn
  {
    code: "interviews.view",
    labelVi: "Xem lịch phỏng vấn",
    labelEn: "View Interviews",
    category: "Phỏng vấn (Interviews)",
  },
  {
    code: "interviews.manage",
    labelVi: "Lên lịch và điều chỉnh phỏng vấn",
    labelEn: "Manage Interviews",
    category: "Phỏng vấn (Interviews)",
  },
  {
    code: "interviews.status",
    labelVi: "Cập nhật trạng thái vòng phỏng vấn",
    labelEn: "Update Interview Status",
    category: "Phỏng vấn (Interviews)",
  },
  {
    code: "interviews.participants",
    labelVi: "Quản lý hội đồng phỏng vấn",
    labelEn: "Manage Interview Participants",
    category: "Phỏng vấn (Interviews)",
  },
  {
    code: "interviews.documents",
    labelVi: "Tải tài liệu phỏng vấn",
    labelEn: "Upload Interview Documents",
    category: "Phỏng vấn (Interviews)",
  },
  {
    code: "interviews.email",
    labelVi: "Gửi email phỏng vấn",
    labelEn: "Send Interview Emails",
    category: "Phỏng vấn (Interviews)",
  },
  // Email
  {
    code: "emails.history_view",
    labelVi: "Xem lịch sử gửi email",
    labelEn: "View Email History",
    category: "Email",
  },
  {
    code: "emails.history_delete",
    labelVi: "Xóa nhật ký email thử nghiệm",
    labelEn: "Delete Email History",
    category: "Email",
  },
  // Báo cáo
  {
    code: "reports.view",
    labelVi: "Xem báo cáo phỏng vấn HR",
    labelEn: "View HR Reports",
    category: "Báo cáo (Reports)",
  },
  {
    code: "reports.manage_status",
    labelVi: "Duyệt / Từ chối kết quả báo cáo",
    labelEn: "Manage Report Decision",
    category: "Báo cáo (Reports)",
  },
  {
    code: "reports.visibility",
    labelVi: "Đóng / Mở quyền xem của hội đồng",
    labelEn: "Toggle Report Visibility",
    category: "Báo cáo (Reports)",
  },
  {
    code: "reports.edit_interviewer",
    labelVi: "Sửa nội dung báo cáo hội đồng",
    labelEn: "Edit Interviewer Report",
    category: "Báo cáo (Reports)",
  },
  {
    code: "reports.delete",
    labelVi: "Xóa báo cáo phỏng vấn",
    labelEn: "Delete Reports",
    category: "Báo cáo (Reports)",
  },
  // Danh mục
  {
    code: "master_data.manage",
    labelVi: "Quản lý danh mục nghiệp vụ",
    labelEn: "Manage Master Data",
    category: "Danh mục (Master Data)",
  },
  // Nhân sự
  {
    code: "users.directory_read",
    labelVi: "Xem danh bạ nhân sự nội bộ",
    labelEn: "Read Internal Directory",
    category: "Người dùng (Users)",
  },
  {
    code: "users.directory_manage",
    labelVi: "Quản lý danh bạ nhân sự",
    labelEn: "Manage Internal Directory",
    category: "Người dùng (Users)",
  },
];

export async function listInternalUsersAction(
  includeInactive = true,
  deps: UserCommandDeps = {},
): Promise<
  | { success: true; data: InternalUserDirectoryRecord[] }
  | { success: false; error: string; code?: string }
> {
  try {
    const supabase = deps.client ?? (await createServerClient());
    const session = await (deps.resolveActor
      ? null
      : getServerSession(supabase));

    if (session && !session.user?.isInternal) {
      return {
        success: false,
        error: "Bạn không có quyền truy cập.",
        code: "FORBIDDEN",
      };
    }

    const { data, error } = await supabase.rpc("list_internal_user_directory", {
      p_include_inactive: includeInactive,
    });

    if (error) {
      return { success: false, error: error.message, code: "INTERNAL_ERROR" };
    }

    const records: InternalUserDirectoryRecord[] = (data || []).map(
      (row: {
        app_user_id: string;
        email: string;
        full_name: string;
        job_title: string | null;
        unit_id: string | null;
        is_active: boolean;
        is_root_admin: boolean;
        is_hr: boolean;
        identity_bound: boolean;
        version_no: number;
      }) => ({
        appUserId: row.app_user_id,
        email: row.email,
        fullName: row.full_name,
        jobTitle: row.job_title,
        unitId: row.unit_id,
        isActive: row.is_active,
        isRootAdmin: row.is_root_admin,
        isHr: row.is_hr,
        identityBound: row.identity_bound,
        versionNo: Number(row.version_no),
      }),
    );

    return { success: true, data: records };
  } catch (error) {
    return {
      success: false,
      error:
        error instanceof Error ? error.message : "Lỗi tải danh bạ người dùng.",
      code: "INTERNAL_ERROR",
    };
  }
}

export async function getUserPermissionsAction(
  targetUserId: string,
  deps: UserCommandDeps = {},
): Promise<
  | { success: true; data: string[] }
  | { success: false; error: string; code?: string }
> {
  try {
    const supabase = deps.client ?? (await createServerClient());
    const { data, error } = await supabase
      .from("app_user_permissions")
      .select("permission_code")
      .eq("app_user_id", targetUserId);

    if (error) {
      return { success: false, error: error.message, code: "INTERNAL_ERROR" };
    }

    const codes = (data || []).map(
      (row: { permission_code: string }) => row.permission_code,
    );
    return { success: true, data: codes };
  } catch (error) {
    return {
      success: false,
      error:
        error instanceof Error ? error.message : "Lỗi tải quyền người dùng.",
      code: "INTERNAL_ERROR",
    };
  }
}

export async function createInternalUserAction(
  payload: {
    email: string;
    fullName: string;
    jobTitle?: string | null;
    unitId?: string | null;
  },
  idempotencyKey?: string,
  deps: UserCommandDeps = {},
): Promise<
  | { success: true; data: CreateInternalUserData }
  | { success: false; error: string; code?: string }
> {
  try {
    const res = await createInternalUser({ ...payload, idempotencyKey }, deps);
    if (!res.success) {
      return {
        success: false,
        error: res.error?.message ?? "Không thể tạo người dùng.",
        code: res.error?.code,
      };
    }
    return { success: true, data: res.data };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : "Lỗi tạo người dùng.",
      code: "INTERNAL_ERROR",
    };
  }
}

export async function updateInternalUserDirectoryAction(
  targetUserId: string,
  patch: {
    fullName?: string | null;
    jobTitle?: string | null;
    unitId?: string | null;
    email?: string | null;
  },
  expectedVersionNo: number,
  idempotencyKey?: string,
  deps: UserCommandDeps = {},
): Promise<
  | { success: true; data: UpdateInternalUserDirectoryData }
  | { success: false; error: string; code?: string }
> {
  try {
    const res = await updateInternalUserDirectory(
      { targetUserId, ...patch, expectedVersionNo, idempotencyKey },
      deps,
    );
    if (!res.success) {
      return {
        success: false,
        error: res.error?.message ?? "Không thể cập nhật người dùng.",
        code: res.error?.code,
      };
    }
    return { success: true, data: res.data };
  } catch (error) {
    return {
      success: false,
      error:
        error instanceof Error ? error.message : "Lỗi cập nhật người dùng.",
      code: "INTERNAL_ERROR",
    };
  }
}

export async function setInternalUserActiveAction(
  targetUserId: string,
  active: boolean,
  expectedVersionNo: number,
  idempotencyKey?: string,
  deps: UserCommandDeps = {},
): Promise<
  | { success: true; data: SetInternalUserActiveData }
  | { success: false; error: string; code?: string }
> {
  try {
    const res = await setInternalUserActive(
      { targetUserId, active, expectedVersionNo, idempotencyKey },
      deps,
    );
    if (!res.success) {
      return {
        success: false,
        error:
          res.error?.message ?? "Không thể thay đổi trạng thái người dùng.",
        code: res.error?.code,
      };
    }
    return { success: true, data: res.data };
  } catch (error) {
    return {
      success: false,
      error:
        error instanceof Error
          ? error.message
          : "Lỗi thay đổi trạng thái người dùng.",
      code: "INTERNAL_ERROR",
    };
  }
}

export async function assignHrRoleAction(
  targetUserId: string,
  expectedVersionNo: number,
  idempotencyKey?: string,
  deps: UserCommandDeps = {},
): Promise<
  | { success: true; data: AssignHrRoleData }
  | { success: false; error: string; code?: string }
> {
  try {
    const res = await assignHrRole(
      { targetUserId, expectedVersionNo, idempotencyKey },
      deps,
    );
    if (!res.success) {
      return {
        success: false,
        error: res.error?.message ?? "Không thể gán vai trò HR.",
        code: res.error?.code,
      };
    }
    return { success: true, data: res.data };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : "Lỗi gán vai trò HR.",
      code: "INTERNAL_ERROR",
    };
  }
}

export async function revokeHrRoleAction(
  targetUserId: string,
  expectedVersionNo: number,
  idempotencyKey?: string,
  deps: UserCommandDeps = {},
): Promise<
  | { success: true; data: RevokeHrRoleData }
  | { success: false; error: string; code?: string }
> {
  try {
    const res = await revokeHrRole(
      { targetUserId, expectedVersionNo, idempotencyKey },
      deps,
    );
    if (!res.success) {
      return {
        success: false,
        error: res.error?.message ?? "Không thể thu hồi vai trò HR.",
        code: res.error?.code,
      };
    }
    return { success: true, data: res.data };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : "Lỗi thu hồi vai trò HR.",
      code: "INTERNAL_ERROR",
    };
  }
}

export async function grantHrPermissionAction(
  targetUserId: string,
  permissionCode: string,
  expectedVersionNo: number,
  idempotencyKey?: string,
  deps: UserCommandDeps = {},
): Promise<
  | { success: true; data: GrantHrPermissionData }
  | { success: false; error: string; code?: string }
> {
  try {
    const res = await grantHrPermission(
      { targetUserId, permissionCode, expectedVersionNo, idempotencyKey },
      deps,
    );
    if (!res.success) {
      return {
        success: false,
        error: res.error?.message ?? "Không thể cấp quyền.",
        code: res.error?.code,
      };
    }
    return { success: true, data: res.data };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : "Lỗi cấp quyền.",
      code: "INTERNAL_ERROR",
    };
  }
}

export async function revokeHrPermissionAction(
  targetUserId: string,
  permissionCode: string,
  expectedVersionNo: number,
  idempotencyKey?: string,
  deps: UserCommandDeps = {},
): Promise<
  | { success: true; data: RevokeHrPermissionData }
  | { success: false; error: string; code?: string }
> {
  try {
    const res = await revokeHrPermission(
      { targetUserId, permissionCode, expectedVersionNo, idempotencyKey },
      deps,
    );
    if (!res.success) {
      return {
        success: false,
        error: res.error?.message ?? "Không thể thu hồi quyền.",
        code: res.error?.code,
      };
    }
    return { success: true, data: res.data };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : "Lỗi thu hồi quyền.",
      code: "INTERNAL_ERROR",
    };
  }
}

export async function getUserManagementDependenciesAction(
  deps: UserCommandDeps = {},
): Promise<{
  units: Array<{ unit_id: string; code: string; name_vi: string }>;
}> {
  const supabase = deps.client ?? (await createServerClient());
  const { data } = await supabase
    .from("organizational_units")
    .select("unit_id, code, name_vi")
    .eq("is_active", true)
    .order("name_vi");

  return {
    units:
      (data as Array<{
        unit_id: string;
        code: string;
        name_vi: string;
      }> | null) || [],
  };
}
