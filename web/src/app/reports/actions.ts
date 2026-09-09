"use server";

import { revalidatePath } from "next/cache";
import {
  loadInterviewerReportPage,
  type SaveInterviewerReportInput,
  saveOwnInterviewerReport,
} from "@/lib/reports/server";

export async function refreshInterviewerReportPageAction() {
  return loadInterviewerReportPage();
}

export async function saveInterviewerReportAction(
  input: SaveInterviewerReportInput,
) {
  const result = await saveOwnInterviewerReport(input);
  if (result.success) revalidatePath("/reports");
  return result;
}
