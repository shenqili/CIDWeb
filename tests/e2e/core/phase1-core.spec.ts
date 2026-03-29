import { expect, test, type Page } from "@playwright/test";

const sampleFile = "D:/CIDWeb/tmp_input/phase1-core-ascii.csv";
const defaultPassword = "CidWeb#2026";

function escapeRegExp(value: string) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

async function login(page: Page, loginName: string, password = defaultPassword) {
  await page.goto("/login", { waitUntil: "networkidle" });
  await page.getByTestId("login-name-input").fill(loginName);
  await page.getByTestId("login-password-input").fill(password);
  await page.getByTestId("login-submit-button").click();
  await page.waitForURL(/\/projects/, { timeout: 30_000 });
}

test.describe("phase1 core", () => {
  test("super admin can see complete multi-brand import summary in the browser", async ({ page }) => {
    await login(page, "superadmin@cid.local");

    await expect(page.getByTestId("projects-total-brands")).toHaveText("9", { timeout: 30_000 });
    await expect(page.getByTestId("projects-total-metrics")).toHaveText("7803");
    await expect(page.locator("[data-testid='projects-summary-table'] tbody tr")).toHaveCount(9);
    await expect(page.locator("[data-testid='projects-summary-table'] tbody tr").first()).toContainText("BDF (brand-bdf)");
    await expect(page.locator("[data-testid='projects-summary-table'] tbody tr").first()).toContainText("1095");
    await expect(page.locator("[data-testid='projects-summary-table'] tbody tr").first()).toContainText("5116");
  });

  test("brand manager only sees the authorized brand and can publish a minimal brand config version", async ({ page }) => {
    await login(page, "manager.brand-bdf@demo.local");
    await page.goto("/brands", { waitUntil: "networkidle" });

    await expect(page.locator("[data-testid='brand-token-list'] .token")).toHaveCount(1);
    await expect(page.locator("[data-testid='brand-token-list'] .token").first()).toContainText("BDF / brand-bdf");

    const versionRows = page.locator("table.data-table").first().locator("tbody tr");
    const versionCountBefore = await versionRows.count();

    await expect(page.getByTestId("brand-minimal-publish-button")).toBeEnabled();
    await page.getByTestId("brand-minimal-publish-button").click();

    await expect(page.getByTestId("brands-notice")).toHaveText(/brand-bdf/, { timeout: 15_000 });
    await expect(versionRows).toHaveCount(versionCountBefore + 1);
    await expect(versionRows.first()).toContainText("published");
  });

  test("super admin can complete dataset create, upload, mapping, key mapping, and publish flow", async ({ page }) => {
    const datasetName = `phase1-browser-${Date.now()}`;

    await login(page, "superadmin@cid.local");
    await page.goto("/data", { waitUntil: "networkidle" });

    const datasetRows = page.locator("[data-testid='dataset-table'] tbody tr");
    const datasetCountBefore = await datasetRows.count();

    await page.getByTestId("dataset-brand-select").selectOption("brand-bdf");
    await page.getByTestId("dataset-name-input").fill(datasetName);
    await page.getByTestId("create-dataset-button").click();

    await expect(page.getByTestId("data-notice")).toHaveText(new RegExp(escapeRegExp(datasetName)), {
      timeout: 15_000,
    });
    await expect(datasetRows).toHaveCount(datasetCountBefore + 1);
    await expect(page.locator("[data-testid='dataset-table'] tbody tr").filter({ hasText: datasetName })).toBeVisible();

    await page.getByTestId("upload-file-input").setInputFiles(sampleFile);
    await expect(page.getByTestId("data-notice")).toHaveText(/phase1-core-ascii\.csv/, { timeout: 15_000 });
    await expect(page.locator("[data-testid='import-batch-list'] li")).toHaveCount(1, { timeout: 15_000 });

    await expect(page.getByTestId("save-field-mappings-button")).toBeEnabled({ timeout: 15_000 });
    await page.getByTestId("save-field-mappings-button").click();
    await expect(page.getByTestId("data-notice")).toHaveText(/3/, { timeout: 15_000 });

    await expect(page.getByTestId("run-primary-key-mapping-button")).toBeEnabled({ timeout: 15_000 });
    await page.getByTestId("run-primary-key-mapping-button").click();
    await expect(page.getByTestId("data-notice")).toContainText("3", { timeout: 15_000 });

    await expect(page.getByTestId("publish-dataset-version-button")).toBeEnabled({ timeout: 15_000 });
    await page.getByTestId("publish-dataset-version-button").click();
    await expect(page.getByTestId("data-notice")).toContainText("v", { timeout: 15_000 });
    await expect(page.locator("[data-testid='dataset-version-list'] .token")).toHaveCount(1, { timeout: 15_000 });
    await expect(page.locator("[data-testid='dataset-version-list'] .token").first()).toContainText("published");
  });

  test("multi-brand analyst can log in, only sees authorized brands, and cannot publish", async ({ page }) => {
    await login(page, "analyst.multi@demo.local");
    await page.goto("/brands", { waitUntil: "networkidle" });

    await expect(page.locator("[data-testid='brand-token-list'] .token")).toHaveCount(2);
    await expect(page.locator("[data-testid='brand-token-list'] .token").nth(0)).toContainText("brand-bdf");
    await expect(page.locator("[data-testid='brand-token-list'] .token").nth(1)).toContainText("brand-estee");
    await expect(page.getByTestId("brand-minimal-publish-button")).toBeDisabled();
  });
});
