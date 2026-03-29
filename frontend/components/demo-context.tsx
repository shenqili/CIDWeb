"use client";

import type { PropsWithChildren } from "react";
import { createContext, useContext, useEffect, useMemo, useState } from "react";

import { API_BASE_URL, AUTH_EXPIRED_EVENT } from "./api";

export type DemoRole = "super_admin" | "tenant_admin" | "brand_manager" | "analyst";

export type UserProfile = {
  userId: string;
  tenantId: string;
  tenantName: string;
  loginName: string;
  displayName: string;
  roles: string[];
  permissions: string[];
  isSuperAdmin: boolean;
  allowedBrandIds: string[];
  activeBrandId?: string | null;
};

type StoredSession = {
  accessToken: string | null;
  user: UserProfile | null;
  activeBrandId: string | null;
};

export type DemoSession = {
  accessToken: string | null;
  activeBrandId: string | null;
  role: DemoRole;
  brandCode: string;
};

type DemoContextValue = DemoSession & {
  user: UserProfile | null;
  isReady: boolean;
  isAuthenticated: boolean;
  tenantName: string;
  displayName: string;
  permissions: string[];
  allowedBrandIds: string[];
  login: (loginName: string, password: string) => Promise<void>;
  logout: () => void;
  setBrandCode: (brandCode: string) => void;
  refreshProfile: () => Promise<void>;
};

const STORAGE_KEY = "cidweb-auth-session";
const SESSION_EVENT = "cidweb-auth-session-change";

const DemoSessionContext = createContext<DemoContextValue | null>(null);

function readStoredSession(): StoredSession {
  if (typeof window === "undefined") {
    return { accessToken: null, user: null, activeBrandId: null };
  }

  const raw = window.localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    return { accessToken: null, user: null, activeBrandId: null };
  }

  try {
    const parsed = JSON.parse(raw) as Partial<StoredSession>;
    return {
      accessToken: parsed.accessToken ?? null,
      user: parsed.user ?? null,
      activeBrandId: parsed.activeBrandId ?? parsed.user?.activeBrandId ?? null,
    };
  } catch {
    window.localStorage.removeItem(STORAGE_KEY);
    return { accessToken: null, user: null, activeBrandId: null };
  }
}

function writeStoredSession(session: StoredSession) {
  if (typeof window === "undefined") {
    return;
  }

  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
  window.dispatchEvent(new Event(SESSION_EVENT));
}

function clearStoredSession() {
  if (typeof window === "undefined") {
    return;
  }

  window.localStorage.removeItem(STORAGE_KEY);
  window.dispatchEvent(new Event(SESSION_EVENT));
}

async function fetchUserProfile(accessToken: string, activeBrandId: string | null): Promise<UserProfile> {
  const headers = new Headers({ Authorization: `Bearer ${accessToken}` });
  if (activeBrandId) {
    headers.set("x-active-brand-code", activeBrandId);
  }

  const response = await fetch(`${API_BASE_URL}/auth/me`, {
    headers,
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("加载用户信息失败");
  }

  return (await response.json()) as UserProfile;
}

export function DemoSessionProvider({ children }: PropsWithChildren) {
  const [storedSession, setStoredSession] = useState<StoredSession>({
    accessToken: null,
    user: null,
    activeBrandId: null,
  });
  const [isReady, setIsReady] = useState(false);

  function applySession(nextSession: StoredSession) {
    setStoredSession(nextSession);
    writeStoredSession(nextSession);
  }

  function applyLogout() {
    setStoredSession({ accessToken: null, user: null, activeBrandId: null });
    clearStoredSession();
  }

  async function refreshProfile() {
    const current = readStoredSession();
    if (!current.accessToken) {
      applyLogout();
      return;
    }

    try {
      const user = await fetchUserProfile(current.accessToken, current.activeBrandId);
      applySession({
        accessToken: current.accessToken,
        user,
        activeBrandId: current.activeBrandId ?? user.activeBrandId ?? user.allowedBrandIds[0] ?? null,
      });
    } catch {
      applyLogout();
    }
  }

  async function login(loginName: string, password: string) {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ loginName, password }),
      cache: "no-store",
    });

    if (!response.ok) {
      let message = `登录失败: ${response.status}`;
      try {
        const data = (await response.json()) as { detail?: string };
        if (data.detail) {
          message = data.detail;
        }
      } catch {
        // Keep default message.
      }
      throw new Error(message);
    }

    const payload = (await response.json()) as { accessToken: string; user: UserProfile };
    applySession({
      accessToken: payload.accessToken,
      user: payload.user,
      activeBrandId: payload.user.activeBrandId ?? payload.user.allowedBrandIds[0] ?? null,
    });
  }

  function setBrandCode(brandCode: string) {
    setStoredSession((current) => {
      const next = {
        ...current,
        activeBrandId: brandCode || current.user?.allowedBrandIds[0] || null,
      };
      writeStoredSession(next);
      return next;
    });
  }

  useEffect(() => {
    const syncSession = () => {
      setStoredSession(readStoredSession());
    };

    const handleAuthExpired = () => {
      applyLogout();
    };

    const initial = readStoredSession();
    setStoredSession(initial);
    setIsReady(true);
    if (initial.accessToken) {
      void refreshProfile();
    }

    window.addEventListener("storage", syncSession);
    window.addEventListener(SESSION_EVENT, syncSession);
    window.addEventListener(AUTH_EXPIRED_EVENT, handleAuthExpired);

    return () => {
      window.removeEventListener("storage", syncSession);
      window.removeEventListener(SESSION_EVENT, syncSession);
      window.removeEventListener(AUTH_EXPIRED_EVENT, handleAuthExpired);
    };
  }, []);

  const value = useMemo<DemoContextValue>(() => {
    const role = (storedSession.user?.roles[0] as DemoRole | undefined) ?? "analyst";
    const brandCode =
      storedSession.activeBrandId ?? storedSession.user?.activeBrandId ?? storedSession.user?.allowedBrandIds[0] ?? "";

    return {
      accessToken: storedSession.accessToken,
      activeBrandId: brandCode || null,
      role,
      brandCode,
      user: storedSession.user,
      isReady,
      isAuthenticated: Boolean(storedSession.accessToken && storedSession.user),
      tenantName: storedSession.user?.tenantName ?? "",
      displayName: storedSession.user?.displayName ?? "",
      permissions: storedSession.user?.permissions ?? [],
      allowedBrandIds: storedSession.user?.allowedBrandIds ?? [],
      login,
      logout: applyLogout,
      setBrandCode,
      refreshProfile,
    };
  }, [isReady, storedSession]);

  return <DemoSessionContext.Provider value={value}>{children}</DemoSessionContext.Provider>;
}

export function useDemoSession(): DemoContextValue {
  const context = useContext(DemoSessionContext);
  if (!context) {
    throw new Error("DemoSessionProvider is missing");
  }
  return context;
}
