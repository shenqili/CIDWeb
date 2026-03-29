export const DEMO_PROJECT_ID = "33333333-3333-3333-3333-333333333333";
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1";
export const AUTH_EXPIRED_EVENT = "cidweb-auth-expired";

type ApiError = {
  detail?: string;
};

export type ApiSession = {
  accessToken?: string | null;
  activeBrandId?: string | null;
};

export async function apiRequest<T>(path: string, session: ApiSession, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);

  if (session.accessToken) {
    headers.set("Authorization", `Bearer ${session.accessToken}`);
  }
  if (session.activeBrandId) {
    headers.set("x-active-brand-code", session.activeBrandId);
  }

  const isFormData = typeof FormData !== "undefined" && init.body instanceof FormData;
  if (!isFormData && init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers,
    cache: "no-store",
  });

  if (!response.ok) {
    let message = `请求失败: ${response.status}`;
    try {
      const data = (await response.json()) as ApiError;
      if (data.detail) {
        message = data.detail;
      }
    } catch {
      // Keep default message when response is not JSON.
    }

    if (response.status === 401 && typeof window !== "undefined") {
      window.dispatchEvent(new Event(AUTH_EXPIRED_EVENT));
    }

    throw new Error(message);
  }

  return (await response.json()) as T;
}
