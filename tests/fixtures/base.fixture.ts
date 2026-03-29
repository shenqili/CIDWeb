import { test as base, expect, type APIRequestContext, type Page } from "@playwright/test";

export type SmokeFixtures = {
  appBaseUrl: string;
  apiBaseUrl: string;
  healthPathCandidates: string[];
  gotoHome: (page?: Page) => Promise<void>;
  assertHealthEndpoint: (request?: APIRequestContext) => Promise<{ url: string; status: number }>;
};

const DEFAULT_APP_BASE_URL = "http://127.0.0.1:3000";
const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000";
const DEFAULT_HEALTH_PATHS = ["/api/v1/health", "/health"];

function normalizeBaseUrl(input: string, fallback: string): string {
  const source = input.trim() || fallback;
  return source.replace(/\/$/, "");
}

function normalizeHealthPaths(raw: string | undefined): string[] {
  if (!raw) {
    return DEFAULT_HEALTH_PATHS;
  }

  const parsed = raw
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean)
    .map((item) => (item.startsWith("/") ? item : `/${item}`));

  return parsed.length > 0 ? parsed : DEFAULT_HEALTH_PATHS;
}

export const test = base.extend<SmokeFixtures>({
  appBaseUrl: async ({ baseURL }, use) => {
    const fallback = baseURL ?? DEFAULT_APP_BASE_URL;
    await use(normalizeBaseUrl(process.env.PLAYWRIGHT_APP_BASE_URL ?? "", fallback));
  },

  apiBaseUrl: async ({}, use) => {
    const configured = process.env.PLAYWRIGHT_API_BASE_URL ?? "";
    await use(normalizeBaseUrl(configured, DEFAULT_API_BASE_URL));
  },

  healthPathCandidates: async ({}, use) => {
    await use(normalizeHealthPaths(process.env.PLAYWRIGHT_HEALTH_PATHS));
  },

  gotoHome: async ({ page, appBaseUrl }, use) => {
    await use(async (targetPage = page) => {
      const response = await targetPage.goto(appBaseUrl, { waitUntil: "domcontentloaded" });
      expect(response, `failed to open homepage: ${appBaseUrl}`).not.toBeNull();

      const status = response?.status() ?? 0;
      expect(status, `homepage returned unexpected status ${status}`).toBeGreaterThanOrEqual(200);
      expect(status, `homepage returned unexpected status ${status}`).toBeLessThan(400);
    });
  },

  assertHealthEndpoint: async ({ request, apiBaseUrl, healthPathCandidates }, use) => {
    await use(async (client = request) => {
      let lastStatus = 0;

      for (const path of healthPathCandidates) {
        const url = `${apiBaseUrl}${path}`;
        const response = await client.get(url);
        const status = response.status();
        lastStatus = status;

        if (status >= 200 && status < 400) {
          return { url, status };
        }
      }

      throw new Error(
        `health endpoint is not reachable. base=${apiBaseUrl}, paths=${healthPathCandidates.join(",")}, lastStatus=${lastStatus}`,
      );
    });
  },
});

export { expect };
