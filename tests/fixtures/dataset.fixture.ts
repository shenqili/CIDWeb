import { test as base } from "@playwright/test";

export type DatasetFixtures = {
  uploadDatasetFile: (absoluteFilePath: string) => Promise<void>;
  publishDatasetVersion: () => Promise<void>;
};

export const test = base.extend<DatasetFixtures>({
  uploadDatasetFile: async ({}, use) => {
    await use(async () => {
      // Skeleton only: upload flow requires finalized page objects and API contracts.
    });
  },

  publishDatasetVersion: async ({}, use) => {
    await use(async () => {
      // Skeleton only: version publish flow will be implemented in phase 2.
    });
  },
});

export { expect } from "@playwright/test";
