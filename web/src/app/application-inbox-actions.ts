"use server";

import type { ApplicationInboxFilters } from "@/lib/application-inbox/model";
import {
  type ApplicationInboxReadResult,
  loadApplicationInbox,
} from "@/lib/application-inbox/server";

export async function queryApplicationInbox(input: {
  filters: ApplicationInboxFilters;
  page: number;
}): Promise<ApplicationInboxReadResult> {
  return loadApplicationInbox({ filters: input.filters, page: input.page });
}
