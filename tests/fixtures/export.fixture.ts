import { test as base } from "@playwright/test";

export type ExportFixtures = {
  createExportRequest: () => Promise<void>;
  approveExportRequest: (requestId: string) => Promise<void>;
};

export const test = base.extend<ExportFixtures>({
  createExportRequest: async ({}, use) => {
    await use(async () => {
      // Skeleton only: export request creation requires stable API and selectors.
    });
  },

  approveExportRequest: async ({}, use) => {
    await use(async () => {
      // Skeleton only: approval flow will be implemented with role state files.
    });
  },
});

export { expect } from "@playwright/test";
