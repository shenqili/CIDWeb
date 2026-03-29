import Link from "next/link";

export default function DashboardPage() {
  return (
    <main className="page">
      <div className="page-heading">
        <div>
          <h1>工作台</h1>
          <p className="lead">
            当前阶段聚焦阶段 1 的核心闭环。请先验证品牌权限和品牌配置版本，再进入数据链路完成上传、映射和版本发布。
          </p>
        </div>
      </div>

      <section className="card-grid">
        <article className="card">
          <h2>项目</h2>
          <div className="metric">1</div>
          <p className="lead">多品牌演示项目已绑定默认 Version Bundle。</p>
        </article>
        <article className="card">
          <h2>阶段 1 目标</h2>
          <div className="metric">5</div>
          <p className="lead">权限、品牌版本、字段映射、主键映射、数据版本发布。</p>
        </article>
        <article className="card">
          <h2>验收方式</h2>
          <div className="metric">E2E</div>
          <p className="lead">浏览器端到端执行 smoke + core，并基于真实链路输出阶段报告。</p>
        </article>
      </section>

      <section className="layout-two">
        <article className="panel">
          <h2>当前阶段重点</h2>
          <ul className="list">
            <li>品牌用户只能看到被授权品牌</li>
            <li>品牌配置版本发布后更新默认 Version Bundle</li>
            <li>上传文件后完成字段映射和主键映射</li>
            <li>生成并发布 Dataset Version</li>
          </ul>
        </article>
        <article className="panel">
          <h2>立即进入</h2>
          <div className="cta-row">
            <Link className="button" href="/brands">
              先验权限与品牌配置
            </Link>
            <Link className="button secondary" href="/data">
              再验数据接入链路
            </Link>
          </div>
        </article>
      </section>
    </main>
  );
}
