"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import { useDemoSession } from "../../components/demo-context";

const SAMPLE_ACCOUNTS = [
  { loginName: "superadmin@cid.local", role: "超级管理员", scope: "9 个品牌" },
  { loginName: "tenantadmin@demo.local", role: "租户管理员", scope: "9 个品牌" },
  { loginName: "analyst.multi@demo.local", role: "多品牌分析师", scope: "brand-bdf, brand-estee" },
  { loginName: "manager.brand-bdf@demo.local", role: "品牌管理员", scope: "brand-bdf" },
];

export default function LoginPage() {
  const router = useRouter();
  const session = useDemoSession();
  const [loginName, setLoginName] = useState("superadmin@cid.local");
  const [password, setPassword] = useState("CidWeb#2026");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);
    setError("");
    try {
      await session.login(loginName, password);
      router.replace("/projects");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "登录失败");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="login-page">
      <section className="login-hero">
        <div className="login-badge">CIDWeb / Stage 1</div>
        <h1>真实账号登录</h1>
        <p>
          当前环境已接入真实账号、角色权限和品牌范围控制。登录后可直接在浏览器里验证超级管理员、租户管理员、
          品牌管理员与多品牌分析师的可见范围和操作权限。
        </p>
      </section>

      <section className="login-card">
        <form className="login-form" onSubmit={handleSubmit}>
          <div>
            <h2>登录平台</h2>
            <p className="lead">默认测试密码统一为 `CidWeb#2026`。</p>
          </div>

          <label className="field-block">
            <span>账号</span>
            <input
              data-testid="login-name-input"
              autoComplete="username"
              value={loginName}
              onChange={(event) => setLoginName(event.target.value)}
            />
          </label>

          <label className="field-block">
            <span>密码</span>
            <input
              data-testid="login-password-input"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />
          </label>

          {error ? (
            <div className="notice error" data-testid="login-error">
              {error}
            </div>
          ) : null}

          <button className="button login-submit" data-testid="login-submit-button" type="submit" disabled={isSubmitting}>
            {isSubmitting ? "登录中..." : "登录并进入系统"}
          </button>
        </form>

        <div className="login-panel">
          <h3>内置账号</h3>
          <ul className="token-list">
            {SAMPLE_ACCOUNTS.map((account) => (
              <li
                key={account.loginName}
                className="token login-account"
                onClick={() => {
                  setLoginName(account.loginName);
                  setPassword("CidWeb#2026");
                }}
              >
                <strong>{account.loginName}</strong>
                <span>{account.role}</span>
                <span>{account.scope}</span>
              </li>
            ))}
          </ul>
          <p className="lead">其余品牌管理员账号遵循 `manager.&lt;brand-code&gt;@demo.local` 规则。</p>
        </div>
      </section>
    </main>
  );
}
