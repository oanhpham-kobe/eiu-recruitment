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

export type InspectedUpload = {
  actualSizeBytes: number;
  checksumSha256: string;
  detectedMimeType: string;
  magicBytesVerified: boolean;
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

function containsAscii(bytes: Uint8Array, value: string): boolean {
  for (let start = 0; start <= bytes.length - value.length; start += 1) {
    let matches = true;
    for (let index = 0; index < value.length; index += 1) {
      if (bytes[start + index] !== value.charCodeAt(index)) {
        matches = false;
        break;
      }
    }
    if (matches) return true;
  }
  return false;
}

function containsUtf16Le(bytes: Uint8Array, value: string): boolean {
  const byteLength = value.length * 2;
  for (let start = 0; start <= bytes.length - byteLength; start += 1) {
    let matches = true;
    for (let index = 0; index < value.length; index += 1) {
      if (
        bytes[start + index * 2] !== value.charCodeAt(index) ||
        bytes[start + index * 2 + 1] !== 0
      ) {
        matches = false;
        break;
      }
    }
    if (matches) return true;
  }
  return false;
}

export function detectUploadMimeType(bytes: Uint8Array): string | null {
  if (new TextDecoder().decode(bytes.slice(0, 5)) === "%PDF-") {
    return MIME_BY_EXTENSION.pdf;
  }
  if (hasPrefix(bytes, [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a])) {
    return MIME_BY_EXTENSION.png;
  }
  if (hasPrefix(bytes, [0xff, 0xd8, 0xff])) {
    return MIME_BY_EXTENSION.jpg;
  }

  if (hasPrefix(bytes, [0x50, 0x4b, 0x03, 0x04])) {
    if (
      containsAscii(bytes, "[Content_Types].xml") &&
      containsAscii(bytes, "word/")
    ) {
      return MIME_BY_EXTENSION.docx;
    }
    if (
      containsAscii(bytes, "[Content_Types].xml") &&
      containsAscii(bytes, "ppt/")
    ) {
      return MIME_BY_EXTENSION.pptx;
    }
    return null;
  }

  if (hasPrefix(bytes, [0xd0, 0xcf, 0x11, 0xe0])) {
    if (
      containsAscii(bytes, "WordDocument") ||
      containsUtf16Le(bytes, "WordDocument")
    ) {
      return MIME_BY_EXTENSION.doc;
    }
    if (
      containsAscii(bytes, "PowerPoint Document") ||
      containsUtf16Le(bytes, "PowerPoint Document")
    ) {
      return MIME_BY_EXTENSION.ppt;
    }
  }
  return null;
}

export async function inspectUploadReservation(
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
  const detectedMimeType = detectUploadMimeType(bytes) ?? "";
  const magicBytesVerified = Boolean(
    extension &&
      detectedMimeType &&
      isAllowedMimeForExtension(extension, detectedMimeType),
  );
  const checksumSha256 = createHash("sha256").update(bytes).digest("hex");
  return {
    success: true,
    data: {
      actualSizeBytes,
      checksumSha256,
      detectedMimeType,
      magicBytesVerified,
    },
  };
}
