import { test as base } from "@playwright/test";

export type ProjectFixtures = {
  selectProject: (projectName: string) => Promise<void>;
  ensureProjectContext: () => Promise<void>;
};

export const test = base.extend<ProjectFixtures>({
  selectProject: async ({}, use) => {
    await use(async () => {
      // Skeleton only: project switch helper depends on finalized project UI structure.
    });
  },

  ensureProjectContext: async ({}, use) => {
    await use(async () => {
      // Skeleton only: context assertion helper will be filled in with real state checks.
    });
  },
});

export { expect } from "@playwright/test";
