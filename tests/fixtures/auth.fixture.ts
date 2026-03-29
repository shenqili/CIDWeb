import { test as base, expect, type Page } from "@playwright/test";

export type UserRole = "super-admin" | "tenant-admin" | "brand-config-admin" | "uploader" | "analyst";

type Credentials = {
  loginName: string;
  password: string;
};

const ACCOUNT_MAP: Record<UserRole, Credentials> = {
  "super-admin": { loginName: "superadmin@cid.local", password: "CidWeb#2026" },
  "tenant-admin": { loginName: "tenantadmin@demo.local", password: "CidWeb#2026" },
  "brand-config-admin": { loginName: "manager.brand-bdf@demo.local", password: "CidWeb#2026" },
  uploader: { loginName: "manager.brand-bdf@demo.local", password: "CidWeb#2026" },
  analyst: { loginName: "analyst.multi@demo.local", password: "CidWeb#2026" },
};

async function loginThroughUi(page: Page, credentials: Credentials) {
  await page.goto("/login", { waitUntil: "networkidle" });
  await page.getByTestId("login-name-input").fill(credentials.loginName);
  await page.getByTestId("login-password-input").fill(credentials.password);
  await page.getByTestId("login-submit-button").click();
  await page.waitForURL(/\/(projects|$)/, { timeout: 30_000 });
}

export type AuthFixtures = {
  loginAs: (role: UserRole) => Promise<void>;
  logout: () => Promise<void>;
};

export const test = base.extend<AuthFixtures>({
  loginAs: async ({ page }, use) => {
    await use(async (role) => {
      await loginThroughUi(page, ACCOUNT_MAP[role]);
    });
  },

  logout: async ({ page }, use) => {
    await use(async () => {
      await page.getByTestId("logout-button").click();
      await expect(page).toHaveURL(/\/login/);
    });
  },
});

export { expect } from "@playwright/test";
