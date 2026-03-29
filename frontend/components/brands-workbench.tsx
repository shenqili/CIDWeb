"use client";

import { useEffect, useState } from "react";

import { apiRequest, DEMO_PROJECT_ID } from "./api";
import { useDemoSession } from "./demo-context";

type Brand = {
  id: string;
  code: string;
  name: string;
  status: string;
};

type BrandConfigVersion = {
  id: string;
  brandId: string;
  versionNo: string;
  status: string;
  publishedAt?: string | null;
};

type VersionBundle = {
  id: string;
  projectId: string;
  brandId: string;
  brandConfigVersionId: string;
  metricCatalogVersionId: string;
  questionnaireTemplateVersionId: string;
  isActive: boolean;
};

type UserProfile = {
  displayName: string;
  roles: string[];
  allowedBrandIds: string[];
  permissions?: string[];
};

type BrandPublishResponse = {
  brandId: string;
  brandCode: string;
  brandConfigVersionId: string;
  versionNo: string;
  status: string;
  affectedProjectCount: number;
  affectedVersionBundleIds: string[];
};

export function BrandsWorkbench() {
  const session = useDemoSession();
  const canPublish = session.permissions.includes("brand.config.publish");
  const [brands, setBrands] = useState<Brand[]>([]);
  const [selectedBrandId, setSelectedBrandId] = useState("");
  const [versions, setVersions] = useState<BrandConfigVersion[]>([]);
  const [bundles, setBundles] = useState<VersionBundle[]>([]);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [message, setMessage] = useState("正在加载品牌配置数据...");
  const [error, setError] = useState("");
  const [isPublishing, setIsPublishing] = useState(false);

  async function loadBaseData() {
    setError("");
    const [brandData, bundleData, profileData] = await Promise.all([
      apiRequest<{ items: Brand[] }>("/brands", session),
      apiRequest<{ items: VersionBundle[] }>(`/projects/${DEMO_PROJECT_ID}/version-bundles`, session),
      apiRequest<UserProfile>("/auth/me", session),
    ]);

    setBrands(brandData.items);
    setBundles(bundleData.items);
    setProfile(profileData);
    setSelectedBrandId((current) =>
      current && brandData.items.some((brand) => brand.id === current) ? current : brandData.items[0]?.id || "",
    );
    setMessage(`当前可见品牌 ${brandData.items.length} 个。`);
  }

  async function loadVersions(brandId: string) {
    if (!brandId) {
      setVersions([]);
      return;
    }

    const data = await apiRequest<{ items: BrandConfigVersion[] }>(`/brands/${brandId}/config-versions`, session);
    setVersions(data.items);
  }

  useEffect(() => {
    void loadBaseData();
  }, [session.role, session.brandCode]);

  useEffect(() => {
    void loadVersions(selectedBrandId);
  }, [selectedBrandId, session.role, session.brandCode]);

  async function handlePublish() {
    if (!selectedBrandId) {
      return;
    }

    setIsPublishing(true);
    setError("");
    try {
      const result = await apiRequest<BrandPublishResponse>(
        `/brands/${selectedBrandId}/config-versions/minimal-publish`,
        session,
        { method: "POST" },
      );
      await loadBaseData();
      await loadVersions(selectedBrandId);
      setMessage(
        `已发布 ${result.brandCode} 的新品牌配置版本 ${result.versionNo}，并更新 ${result.affectedProjectCount} 个项目绑定。`,
      );
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "品牌配置发布失败");
    } finally {
      setIsPublishing(false);
    }
  }

  return (
    <main className="page">
      <div className="page-heading">
        <div>
          <h1>品牌配置</h1>
          <p className="lead">验证品牌用户权限、品牌配置版本最小发布链路，以及项目绑定到最新 Version Bundle 的结果。</p>
        </div>
        <button
          className="button"
          data-testid="brand-minimal-publish-button"
          onClick={handlePublish}
          disabled={!selectedBrandId || isPublishing || !canPublish}
        >
          {isPublishing ? "发布中..." : "发布最小品牌配置版本"}
        </button>
      </div>

      {error ? (
        <div className="notice error" data-testid="brands-notice">
          {error}
        </div>
      ) : (
        <div className="notice success" data-testid="brands-notice">
          {message}
        </div>
      )}

      <section className="layout-two">
        <article className="panel">
          <h2>当前权限视图</h2>
          <div className="stack">
            <div className="kv">
              <span>当前用户</span>
              <strong>{profile?.displayName ?? "-"}</strong>
            </div>
            <div className="kv">
              <span>角色</span>
              <strong>{profile?.roles.join(", ") ?? "-"}</strong>
            </div>
            <div className="kv">
              <span>授权品牌</span>
              <strong>{profile?.allowedBrandIds.join(", ") ?? "-"}</strong>
            </div>
          </div>
        </article>

        <article className="panel">
          <h2>可操作品牌</h2>
          <label className="field-block">
            <span>选择品牌</span>
            <select
              data-testid="brand-select"
              value={selectedBrandId}
              onChange={(event) => setSelectedBrandId(event.target.value)}
            >
              {brands.map((brand) => (
                <option key={brand.id} value={brand.id}>
                  {brand.name} ({brand.code})
                </option>
              ))}
            </select>
          </label>
          <ul className="token-list" data-testid="brand-token-list">
            {brands.map((brand) => (
              <li key={brand.id} className="token">
                {brand.name} / {brand.code}
              </li>
            ))}
          </ul>
        </article>
      </section>

      <section className="layout-two">
        <article className="panel">
          <h2>品牌配置版本</h2>
          <table className="data-table">
            <thead>
              <tr>
                <th>版本号</th>
                <th>状态</th>
                <th>发布时间</th>
              </tr>
            </thead>
            <tbody>
              {versions.map((version) => (
                <tr key={version.id}>
                  <td>{version.versionNo}</td>
                  <td>{version.status}</td>
                  <td>{version.publishedAt ?? "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </article>

        <article className="panel">
          <h2>当前项目 Version Bundle</h2>
          <table className="data-table">
            <thead>
              <tr>
                <th>品牌</th>
                <th>品牌配置版本</th>
                <th>是否激活</th>
              </tr>
            </thead>
            <tbody>
              {bundles.map((bundle) => (
                <tr key={bundle.id}>
                  <td>{bundle.brandId}</td>
                  <td>{bundle.brandConfigVersionId}</td>
                  <td>{bundle.isActive ? "是" : "否"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </article>
      </section>
    </main>
  );
}
