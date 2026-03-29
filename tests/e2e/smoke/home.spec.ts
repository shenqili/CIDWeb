import { expect, test } from "@playwright/test";

test("unauthenticated homepage redirects to login", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveURL(/\/login/);
  await expect(page.getByRole("heading", { name: "真实账号登录" })).toBeVisible();
});
