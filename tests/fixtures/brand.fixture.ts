import { test as base } from "@playwright/test";

export type BrandFixtures = {
  selectBrand: (brandName: string) => Promise<void>;
  currentBrandName: () => Promise<string | null>;
};

export const test = base.extend<BrandFixtures>({
  selectBrand: async ({}, use) => {
    await use(async () => {
      // Skeleton only: UI brand switch helper will be implemented with real selectors.
    });
  },

  currentBrandName: async ({}, use) => {
    await use(async () => null);
  },
});

export { expect } from "@playwright/test";
