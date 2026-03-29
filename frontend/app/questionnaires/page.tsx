export default function QuestionnairesPage() {
  return (
    <main className="page">
      <div>
        <h1>问卷</h1>
        <p className="lead">阶段 3 将补齐模板管理、外部填写、历史导入和计分结果回写。</p>
      </div>
      <section className="card-grid">
        <article className="card">
          <h2>模板管理</h2>
          <p className="lead">题型、逻辑和计分规则。</p>
        </article>
        <article className="card">
          <h2>问卷发放</h2>
          <p className="lead">链接、二维码和有效期。</p>
        </article>
        <article className="card">
          <h2>历史导入</h2>
          <p className="lead">Excel 批量导入历史答卷结果。</p>
        </article>
      </section>
    </main>
  );
}
