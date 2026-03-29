export default function TasksPage() {
  return (
    <main className="page">
      <div>
        <h1>任务中心</h1>
        <p className="lead">阶段 2 起将在这里统一查看导入任务、分析任务、导出任务和失败日志。</p>
      </div>
      <section className="layout-two">
        <article className="panel">
          <h2>任务状态</h2>
          <ul className="list">
            <li>queued</li>
            <li>running</li>
            <li>partial_success</li>
            <li>failed</li>
          </ul>
        </article>
        <article className="panel">
          <h2>日志与重试</h2>
          <p className="lead">当前阶段保留布局，等待任务编排接入。</p>
        </article>
      </section>
    </main>
  );
}
