import { expect, test } from "@playwright/test";

const apiBase = process.env.API_BASE_URL ?? "http://127.0.0.1:8000/api/v1";

test("health endpoint responds with ok", async ({ request }) => {
  const response = await request.get(`${apiBase}/health`);
  expect(response.ok()).toBeTruthy();
  const data = await response.json();
  expect(data.status).toBe("ok");
});
