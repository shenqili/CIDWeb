"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import type { PropsWithChildren } from "react";
import { useEffect } from "react";

import { useDemoSession } from "./demo-context";

const navItems = [
  { href: "/", label: "工作台" },
  { href: "/projects", label: "项目" },
  { href: "/brands", label: "品牌配置" },
  { href: "/data", label: "数据" },
  { href: "/analysis", label: "分析" },
  { href: "/questionnaires", label: "问卷" },
  { href: "/tasks", label: "任务中心" },
];

export function AppShell({ children }: PropsWithChildren) {
  const pathname = usePathname();
  const router = useRouter();
  const session = useDemoSession();

  useEffect(() => {
    if (!session.isReady) {
      return;
    }

    if (!session.isAuthenticated && pathname !== "/login") {
      router.replace("/login");
      return;
    }

    if (session.isAuthenticated && pathname === "/login") {
      router.replace("/projects");
    }
  }, [pathname, router, session.isAuthenticated, session.isReady]);

  if (pathname === "/login") {
    if (!session.isReady || session.isAuthenticated) {
      return <div className="page-loading">正在准备登录环境...</div>;
    }
    return <>{children}</>;
  }

  if (!session.isReady || !session.isAuthenticated) {
    return <div className="page-loading">正在校验登录状态...</div>;
  }

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">CIDWeb</div>
        <nav aria-label="Primary">
          {navItems.map((item) => {
            const active = pathname === item.href;
            return (
              <Link key={item.href} href={item.href} className={active ? "active" : undefined}>
                {item.label}
              </Link>
            );
          })}
        </nav>
      </aside>
      <div className="content">
        <header className="topbar">
          <div className="topbar-title">
            <strong>企业级皮肤大数据管理与智能分析平台</strong>
            <span className="topbar-subtitle">阶段 1 真实账号演示环境</span>
          </div>
          <div className="context-panel">
            <div className="context-actions">
              <label className="field-inline">
                <span>当前品牌</span>
                <select
                  aria-label="当前品牌"
                  data-testid="active-brand-select"
                  value={session.brandCode}
                  onChange={(event) => session.setBrandCode(event.target.value)}
                  disabled={session.allowedBrandIds.length <= 1}
                >
                  {session.allowedBrandIds.map((brandCode) => (
                    <option key={brandCode} value={brandCode}>
                      {brandCode}
                    </option>
                  ))}
                </select>
              </label>
              <button className="button secondary" data-testid="logout-button" onClick={session.logout}>
                退出登录
              </button>
            </div>
            <div className="context">
              <span className="pill">租户: {session.tenantName}</span>
              <span className="pill">账号: {session.displayName}</span>
              <span className="pill">角色: {session.user?.roles.join(", ")}</span>
              <span className="pill">品牌范围: {session.allowedBrandIds.join(", ")}</span>
            </div>
          </div>
        </header>
        {children}
      </div>
    </div>
  );
}
