import { test as base } from "@playwright/test";

export type TaskFixtures = {
  waitForTaskDone: (taskId: string, timeoutMs?: number) => Promise<void>;
};

export const test = base.extend<TaskFixtures>({
  waitForTaskDone: async ({}, use) => {
    await use(async () => {
      // Skeleton only: polling strategy will be implemented when task APIs are finalized.
    });
  },
});

export { expect } from "@playwright/test";
