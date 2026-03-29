export default function AnalysisPage() {
  return (
    <main className="page">
      <div>
        <h1>分析</h1>
        <p className="lead">阶段 2 将在这里补齐快速分析、高级分析和派生变量发布链路。</p>
      </div>
      <section className="layout-three">
        <article className="panel">
          <h2>左侧配置</h2>
          <ul className="list">
            <li>品牌</li>
            <li>数据版本</li>
            <li>分析目标</li>
          </ul>
        </article>
        <article className="panel">
          <h2>方法工作区</h2>
          <p className="status">当前阶段保留结构占位，等待阶段 2 接入真实分析任务。</p>
        </article>
        <article className="panel">
          <h2>结果摘要</h2>
          <p className="lead">分析运行后在这里展示主图、主表和关键解释。</p>
        </article>
      </section>
    </main>
  );
}
