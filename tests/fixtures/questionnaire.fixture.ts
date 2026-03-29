import { test as base } from "@playwright/test";

export type QuestionnaireFixtures = {
  openPublicQuestionnaire: (publicLink: string) => Promise<void>;
  importHistoryQuestionnaire: (absoluteFilePath: string) => Promise<void>;
};

export const test = base.extend<QuestionnaireFixtures>({
  openPublicQuestionnaire: async ({}, use) => {
    await use(async () => {
      // Skeleton only: public questionnaire flow depends on released questionnaire pages.
    });
  },

  importHistoryQuestionnaire: async ({}, use) => {
    await use(async () => {
      // Skeleton only: batch import flow needs finalized upload endpoints.
    });
  },
});

export { expect } from "@playwright/test";
