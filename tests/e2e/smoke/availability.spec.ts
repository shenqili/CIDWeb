import { test, expect } from "../../fixtures/base.fixture";

test.describe("smoke: app availability", () => {
  test("homepage should be reachable", async ({ page, gotoHome }) => {
    await gotoHome(page);
    await expect(page).toHaveURL(/http:\/\//);
  });

  test("health endpoint should be reachable", async ({ assertHealthEndpoint }) => {
    const result = await assertHealthEndpoint();
    expect(result.status).toBeGreaterThanOrEqual(200);
    expect(result.status).toBeLessThan(400);
  });
});
