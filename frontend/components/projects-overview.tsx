"use client";

import { useEffect, useState } from "react";

import { apiRequest, DEMO_PROJECT_ID } from "./api";
import { useDemoSession } from "./demo-context";

type PortfolioBrandSummary = {
  brandId: string;
  brandCode: string;
  brandName: string;
  metricCount: number;
  datasetCount: number;
  datasetVersionCount: number;
  maxRowCount: number;
  maxColumnCount: number;
};

type PortfolioSummary = {
  projectId: string;
  totalBrands: number;
  totalMetricMappings: number;
  totalDatasets: number;
  totalDatasetVersions: number;
  items: PortfolioBrandSummary[];
};

export function ProjectsOverview() {
  const session = useDemoSession();
  const [summary, setSummary] = useState<PortfolioSummary | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadSummary() {
      setError("");
      try {
        const data = await apiRequest<PortfolioSummary>(`/projects/${DEMO_PROJECT_ID}/portfolio-summary`, session);
        setSummary(data);
      } catch (caught) {
        setError(caught instanceof Error ? caught.message : "项目总览加载失败");
      }
    }

    void loadSummary();
  }, [session.role, session.brandCode]);

  return (
    <main className="page">
      <div className="page-heading">
        <div>
          <h1>项目</h1>
          <p className="lead">浏览多品牌项目的完整导入结果，确认各品牌指标和项目数据已经挂到统一项目上下文中。</p>
        </div>
      </div>

      {error ? (
        <div className="notice error">{error}</div>
      ) : (
        <div className="notice success" data-testid="projects-summary-notice">
          {summary
            ? `当前可见 ${summary.totalBrands} 个品牌，累计 ${summary.totalMetricMappings} 个指标映射、${summary.totalDatasets} 个数据集、${summary.totalDatasetVersions} 个数据版本。`
            : "正在加载项目总览..."}
        </div>
      )}

      <section className="card-grid">
        <article className="card">
          <h2>品牌数</h2>
          <div className="metric" data-testid="projects-total-brands">
            {summary?.totalBrands ?? "-"}
          </div>
          <p className="lead">当前角色在项目内可见的品牌数量。</p>
        </article>
        <article className="card">
          <h2>指标映射</h2>
          <div className="metric" data-testid="projects-total-metrics">
            {summary?.totalMetricMappings ?? "-"}
          </div>
          <p className="lead">从各家指标工作簿导入的品牌指标总数。</p>
        </article>
        <article className="card">
          <h2>数据版本</h2>
          <div className="metric" data-testid="projects-total-versions">
            {summary?.totalDatasetVersions ?? "-"}
          </div>
          <p className="lead">当前项目下已发布的数据版本总数。</p>
        </article>
      </section>

      <section className="panel">
        <h2>品牌导入总览</h2>
        <table className="data-table" data-testid="projects-summary-table">
          <thead>
            <tr>
              <th>品牌</th>
              <th>指标数</th>
              <th>数据集数</th>
              <th>数据版本数</th>
              <th>最大记录数</th>
              <th>最大字段数</th>
            </tr>
          </thead>
          <tbody>
            {summary?.items.map((item) => (
              <tr key={item.brandId}>
                <td>
                  {item.brandName} ({item.brandCode})
                </td>
                <td>{item.metricCount}</td>
                <td>{item.datasetCount}</td>
                <td>{item.datasetVersionCount}</td>
                <td>{item.maxRowCount}</td>
                <td>{item.maxColumnCount}</td>
              </tr>
            )) ?? null}
          </tbody>
        </table>
      </section>
    </main>
  );
}
