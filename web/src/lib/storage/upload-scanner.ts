import "server-only";

import { createHash } from "node:crypto";
import {
  CANDIDATE_QUARANTINE_FILE_SIZE_LIMIT,
  extractExtension,
  isAllowedMimeForExtension,
} from "@/lib/storage/buckets";
import { createAdminClient } from "@/lib/supabase/admin";

const MIME_BY_EXTENSION: Record<string, string> = {
  pdf: "application/pdf",
  doc: "application/msword",
  docx: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  ppt: "application/vnd.ms-powerpoint",
  pptx: "application/vnd.openxmlformats-officedocument.presentationml.presentation",
  png: "image/png",
  jpg: "image/jpeg",
  jpeg: "image/jpeg",
};

type MalwareScanStatus = "CLEAN" | "INFECTED" | "ERROR";

export type InspectedUpload = {
  actualSizeBytes: number;
  checksumSha256: string;
  detectedMimeType: string;
  magicBytesVerified: boolean;
  malwareScanStatus: MalwareScanStatus;
};

type ScanFailure = {
  success: false;
  code:
    | "MALWARE_SCAN_REQUIRED"
    | "INVALID_CONTENT_SIGNATURE"
    | "UPLOAD_LIMIT_EXCEEDED"
    | "NOT_FOUND"
    | "INTERNAL_ERROR";
  error: string;
};
type ScanSuccess = { success: true; data: InspectedUpload };

function hasPrefix(bytes: Uint8Array, prefix: number[]): boolean {
  return prefix.every((value, index) => bytes[index] === value);
}

function verifyMagic(extension: string, bytes: Uint8Array): boolean {
  switch (extension) {
    case "pdf":
      return new TextDecoder().decode(bytes.slice(0, 5)) === "%PDF-";
    case "png":
      return hasPrefix(bytes, [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
    case "jpg":
    case "jpeg":
      return hasPrefix(bytes, [0xff, 0xd8, 0xff]);
    case "doc":
    case "docx":
    case "ppt":
    case "pptx":
      return (
        hasPrefix(bytes, [0x50, 0x4b, 0x03, 0x04]) ||
        hasPrefix(bytes, [0xd0, 0xcf, 0x11, 0xe0])
      );
    default:
      return false;
  }
}

async function requestMalwareVerdict(
  bytes: Uint8Array,
  filename: string,
): Promise<MalwareScanStatus | null> {
  const scannerUrl = process.env.MALWARE_SCANNER_URL?.trim();
  if (!scannerUrl) return null;

  const headers: Record<string, string> = {
    "content-type": "application/octet-stream",
    "x-original-filename": filename,
  };
  const scannerToken = process.env.MALWARE_SCANNER_TOKEN?.trim();
  if (scannerToken) headers.authorization = `Bearer ${scannerToken}`;

  try {
    const response = await fetch(scannerUrl, {
      method: "POST",
      headers,
      body: Buffer.from(bytes),
      cache: "no-store",
    });
    if (!response.ok) return "ERROR";
    const payload = (await response.json()) as { status?: unknown };
    const status = String(payload.status ?? "").toUpperCase();
    return status === "CLEAN" || status === "INFECTED" || status === "ERROR"
      ? status
      : "ERROR";
  } catch {
    return "ERROR";
  }
}

export async function inspectAndScanUploadReservation(
  reservationId: string,
): Promise<ScanSuccess | ScanFailure> {
  const admin = createAdminClient();
  if (!admin) {
    return {
      success: false,
      code: "MALWARE_SCAN_REQUIRED",
      error: "Trusted upload scanner is not configured",
    };
  }

  const { data: reservation, error: reservationError } = await admin
    .from("upload_reservations")
    .select(
      "temp_bucket, temp_path, original_filename, declared_mime_type, expected_max_size_bytes, status_code",
    )
    .eq("upload_reservation_id", reservationId)
    .maybeSingle();

  if (reservationError || !reservation) {
    return {
      success: false,
      code: "NOT_FOUND" as ScanFailure["code"],
      error: reservationError?.message || "Upload reservation not found",
    };
  }

  if (!["RESERVED", "UPLOADED"].includes(String(reservation.status_code))) {
    return {
      success: false,
      code: "INTERNAL_ERROR",
      error: "Upload reservation is not available for scanning",
    };
  }

  const { data: object, error: downloadError } = await admin.storage
    .from(reservation.temp_bucket)
    .download(reservation.temp_path);
  if (downloadError || !object) {
    return {
      success: false,
      code: "INTERNAL_ERROR",
      error: downloadError?.message || "Uploaded object is not available",
    };
  }

  const bytes = new Uint8Array(await object.arrayBuffer());
  const actualSizeBytes = bytes.byteLength;
  if (
    actualSizeBytes <= 0 ||
    actualSizeBytes > CANDIDATE_QUARANTINE_FILE_SIZE_LIMIT ||
    actualSizeBytes > Number(reservation.expected_max_size_bytes)
  ) {
    return {
      success: false,
      code: "UPLOAD_LIMIT_EXCEEDED",
      error: "Uploaded object exceeds the reserved size limit",
    };
  }

  const extension = extractExtension(reservation.original_filename);
  const detectedMimeType = extension ? MIME_BY_EXTENSION[extension] : "";
  const magicBytesVerified = Boolean(
    extension &&
      detectedMimeType &&
      verifyMagic(extension, bytes) &&
      isAllowedMimeForExtension(extension, detectedMimeType),
  );
  const checksumSha256 = createHash("sha256").update(bytes).digest("hex");
  const malwareScanStatus = await requestMalwareVerdict(
    bytes,
    reservation.original_filename,
  );

  if (!malwareScanStatus) {
    return {
      success: false,
      code: "MALWARE_SCAN_REQUIRED",
      error: "Trusted malware scanner is not configured",
    };
  }

  return {
    success: true,
    data: {
      actualSizeBytes,
      checksumSha256,
      detectedMimeType,
      magicBytesVerified,
      malwareScanStatus,
    },
  };
}
