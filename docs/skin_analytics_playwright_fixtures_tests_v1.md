# 企业级皮肤大数据管理与智能分析平台 Playwright Fixture 与用例骨架方案 v1

## 1. 文档目标

本文件用于在已有：

- `D:\CIDWeb\docs\skin_analytics_playwright_plan_v1.md`
- `D:\CIDWeb\docs\skin_analytics_test_acceptance_plan_v1.md`
- `D:\CIDWeb\docs\skin_analytics_openapi_v1_1.yaml`
- `D:\CIDWeb\docker-compose.demo.yml`

基础上，进一步把浏览器端到端测试落成可执行的 Playwright fixture 与测试骨架方案。

本文件重点覆盖：

- 目录结构
- 角色 `storageState`
- fixture 设计
- spec 粒度建议
- Docker 演示环境准备
- 外部匿名问卷
- 历史问卷导入
- 高敏导出审批

---

## 2. 推荐目录结构

```text
playwright/
  config/
    playwright.config.ts
    projects.config.ts
  storage/
    super-admin.json
    tenant-admin.json
    brand-config-admin.json
    uploader.json
    analyst.json
  fixtures/
    auth.fixture.ts
    tenant.fixture.ts
    project.fixture.ts
    brand.fixture.ts
    dataset.fixture.ts
    questionnaire.fixture.ts
    task.fixture.ts
    export.fixture.ts
  data/
    uploads/
      standard_dataset.xlsx
      rd_conflict_dataset.xlsx
      questionnaire_history.xlsx
    expected/
      analysis/
      exports/
      questionnaires/
  utils/
    api-client.ts
    test-ids.ts
    downloads.ts
    polling.ts
    storage.ts
  scripts/
    prepare-demo-data.ts
    create-storage-state.ts
  e2e/
    auth/
      login.spec.ts
      first-login-reset.spec.ts
    projects/
      project-bootstrap.spec.ts
      brand-bindings.spec.ts
    uploads/
      dataset-upload.spec.ts
      mapping-and-publish.spec.ts
      identifier-conflict.spec.ts
    analysis/
      quick-analysis.spec.ts
      advanced-analysis.spec.ts
      brand-switch.spec.ts
      derived-publish.spec.ts
    exports/
      export-approval.spec.ts
      export-expired.spec.ts
    questionnaires/
      questionnaire-template.spec.ts
      questionnaire-public-anonymous.spec.ts
      questionnaire-history-import.spec.ts
      questionnaire-scoring.spec.ts
    restricted-analytics/
      restricted-aggregate.spec.ts
```

---

## 2.1 `playwright.config.ts` 草案结构

建议包含：

- `testDir: './playwright/e2e'`
- `timeout`
- `expect.timeout`
- `fullyParallel`
- `retries`
- `reporter`
- `use.baseURL`
- `use.trace`
- `use.screenshot`
- `use.video`
- `projects`

推荐项目配置：

- `chromium-smoke`
- `chromium-core`
- `chromium-full`

推荐环境变量：

- `E2E_BASE_URL`
- `E2E_API_BASE_URL`
- `E2E_DOWNLOAD_DIR`
- `E2E_STORAGE_DIR`
- `E2E_ENV_NAME`

---

## 3. 角色 storageState 方案

建议为以下角色分别维护独立状态文件：

- `super-admin.json`
- `tenant-admin.json`
- `brand-config-admin.json`
- `uploader.json`
- `analyst.json`

### 3.1 角色用途

- `super-admin`
  用于平台级受限分析空间、跨租户聚合分析、平台管理检查
- `tenant-admin`
  用于项目创建、高敏导出审批、租户内配置核验
- `brand-config-admin`
  用于品牌配置、问卷模板、模板版本发布
- `uploader`
  用于数据上传、主键映射、版本发布
- `analyst`
  用于快速分析、高级分析、派生变量发布、导出申请

### 3.2 建议生成方式

- 使用全局 setup 登录并保存 `storageState`
- 每个角色单独生成
- 每次环境重置后重新生成

### 3.3 命名规范

建议文件命名包含环境名：

- `demo-super-admin.json`
- `demo-tenant-admin.json`
- `demo-brand-config-admin.json`
- `demo-uploader.json`
- `demo-analyst.json`

---

## 3.4 演示账号准备建议

建议准备以下固定演示账号：

- `super-admin@cidweb.demo`
- `tenant-admin@cidweb.demo`
- `brand-admin@cidweb.demo`
- `uploader@cidweb.demo`
- `analyst@cidweb.demo`

要求：

- 固定初始密码
- 可通过脚本重置
- 与演示租户、品牌、项目权限一一对应

---

## 4. Fixture 设计

### 4.1 `auth.fixture.ts`

职责：

- 根据角色自动加载 `storageState`
- 提供 `loginAs(role)` 能力
- 处理首登改密与会话续期的兼容逻辑

暴露：

- `page`
- `context`
- `currentRole`

### 4.2 `tenant.fixture.ts`

职责：

- 加载当前租户信息
- 断言租户上下文是否正确

暴露：

- `tenantId`
- `tenantName`

### 4.3 `project.fixture.ts`

职责：

- 选择默认演示项目
- 切换项目
- 返回项目基本信息

暴露：

- `projectId`
- `projectName`
- `selectProject(name)`

### 4.4 `brand.fixture.ts`

职责：

- 选择当前品牌
- 检查 `VersionBundle` 是否切换成功
- 断言品牌切换后的上下文状态

暴露：

- `brandId`
- `brandName`
- `switchBrand(name)`
- `assertVersionBundleChanged()`

### 4.5 `dataset.fixture.ts`

职责：

- 提供测试文件路径
- 上传标准数据集
- 上传冲突数据集
- 发布数据版本

暴露：

- `standardDatasetPath`
- `rdConflictDatasetPath`
- `uploadDataset()`
- `publishDatasetVersion()`

### 4.6 `questionnaire.fixture.ts`

职责：

- 打开问卷模板页
- 创建问卷活动
- 获取公开问卷链接
- 上传历史问卷文件

暴露：

- `questionnaireHistoryPath`
- `createCampaign()`
- `openPublicQuestionnaire(token)`
- `importQuestionnaireHistory()`

### 4.7 `task.fixture.ts`

职责：

- 轮询异步任务状态
- 等待任务完成
- 断言任务状态迁移

暴露：

- `waitForTask(taskId)`
- `assertTaskStatus(expected)`

### 4.8 `export.fixture.ts`

职责：

- 发起导出申请
- 审批导出
- 下载并保存导出文件
- 校验下载链接过期

暴露：

- `requestSensitiveExport()`
- `approveExport()`
- `rejectExport()`
- `downloadExport()`

---

## 4.9 Fixture 边界原则

- `auth.fixture.ts` 仅负责认证与角色状态装载
- `project.fixture.ts` 负责项目选择，不负责品牌切换
- `brand.fixture.ts` 负责品牌和 `VersionBundle` 上下文
- `dataset.fixture.ts` 负责上传与数据版本
- `questionnaire.fixture.ts` 负责问卷活动、公开链接、历史导入
- `task.fixture.ts` 负责任务轮询和状态断言
- `export.fixture.ts` 负责审批与下载

---

## 5. Spec 粒度建议

### 5.1 粒度原则

- 一个 spec 聚焦一条主链路
- 避免单个 spec 跨越多个核心域
- 长链路拆成主链路 + 审批链路 + 结果链路

### 5.2 建议粒度

#### `auth/login.spec.ts`

覆盖：

- 正常登录
- 错误密码
- 未授权角色访问受限入口

#### `projects/project-bootstrap.spec.ts`

覆盖：

- 创建项目
- 绑定多品牌
- 绑定 `VersionBundle`

#### `uploads/dataset-upload.spec.ts`

覆盖：

- 标准上传
- 字段映射
- 发布版本

#### `uploads/identifier-conflict.spec.ts`

覆盖：

- `RD` 冲突
- 人工映射
- 审计留痕

#### `analysis/quick-analysis.spec.ts`

覆盖：

- 品牌选择
- 数据版本选择
- 快速分析
- 查看结果

#### `analysis/advanced-analysis.spec.ts`

覆盖：

- 高级变量配置
- 异步任务提交
- 任务中心查看

#### `analysis/brand-switch.spec.ts`

覆盖：

- 多品牌切换
- 不兼容变量清空
- 上下文刷新

#### `analysis/derived-publish.spec.ts`

覆盖：

- 发布派生变量
- 新版本生成
- 新版本详情跳转

#### `exports/export-approval.spec.ts`

覆盖：

- 创建审批单
- 审批通过
- 可下载链接

#### `exports/export-expired.spec.ts`

覆盖：

- 审批拒绝
- 审批过期
- 过期链接不可访问

#### `questionnaires/questionnaire-public-anonymous.spec.ts`

覆盖：

- 外部匿名链接打开
- 填写与提交
- 成功入库
- `pending_match` 行为

#### `questionnaires/questionnaire-history-import.spec.ts`

覆盖：

- 历史问卷 Excel 上传
- 模板识别
- 编号映射
- 导入完成

#### `questionnaires/questionnaire-scoring.spec.ts`

覆盖：

- 反向题
- 多选题
- 跳题逻辑
- 总分与维度分

#### `restricted-analytics/restricted-aggregate.spec.ts`

覆盖：

- 超级管理员进入受限空间
- 跨租户聚合分析
- 仅输出聚合结果

---

## 5.3 smoke / core / full 分层

### `@smoke`

- 登录
- 项目初始化
- 标准上传
- 快速分析
- 结果页打开

### `@core`

- 主键映射冲突
- 品牌切换
- 派生变量发布
- 高敏导出审批通过/拒绝
- 外部匿名问卷提交

### `@full`

- 历史问卷导入
- 高级分析
- 受限分析空间
- 过期链接校验
- 跨模块长链路回归

---

## 6. Docker 演示环境准备

### 6.1 启动前准备

确保以下目录存在：

- `./storage/raw`
- `./storage/intermediate`
- `./storage/exports`
- `./storage/charts`
- `./storage/manifests`
- `./storage/audit-attachments`

### 6.2 启动顺序

按 `docker-compose.demo.yml`：

1. `postgres`
2. `redis`
3. `api`
4. `worker`
5. `scheduler`
6. `frontend`

### 6.3 演示环境建议准备数据

- 一个演示租户
- 两个品牌
- 一个多品牌项目
- 一个已发布数据版本
- 一条高敏导出审批数据
- 一个公开匿名问卷活动
- 一份历史问卷 Excel

---

## 6.4 测试数据目录规范

建议：

- `playwright/data/uploads/standard_dataset.xlsx`
- `playwright/data/uploads/rd_conflict_dataset.xlsx`
- `playwright/data/uploads/questionnaire_history.xlsx`
- `playwright/data/expected/analysis/`
- `playwright/data/expected/exports/`
- `playwright/data/expected/questionnaires/`

原则：

- 一个文件只承担一种测试目的
- 输入文件与预期输出目录一一对应

---

## 7. 关键问卷场景

### 7.1 外部匿名填写

测试重点：

- 通过公开链接打开问卷
- 不依赖登录态
- 正确提交答卷
- `subject_id` 无法映射时进入 `pending_match`
- 页面不显示后台导航
- 过期链接不可继续提交

### 7.2 在线实时答卷

测试重点：

- 页面题目渲染
- 跳题逻辑生效
- 提交后即时计分或进入待计分状态
- 多页问卷暂存与恢复

### 7.3 历史答卷导入

测试重点：

- Excel 文件上传
- 模板版本识别
- `RD / RD- / 微生态编号` 映射
- 失败项异常清单输出

---

## 8. 高敏导出审批场景

### 必测状态流

- `pending_approval`
- `approved`
- `rejected`
- `expired`

### 核心断言

- 申请人与审批人不能相同
- 审批通过后生成下载链接
- 下载次数限制生效
- 过期链接不可访问
- 审批拒绝后允许重新申请

---

## 9. 断言细节建议

### 9.1 品牌切换

- 当前品牌标签更新
- `VersionBundle` 摘要更新
- 不兼容变量被清空
- 兼容模板保留或提示重校验

### 9.2 外部匿名问卷

- 无登录信息
- 提交成功确认态
- `pending_match` 状态可见

### 9.3 历史问卷导入

- 导入任务创建成功
- 模板识别结果正确
- 编号映射结果正确
- 异常清单可下载

### 9.4 高敏导出

- 审批状态从 `pending_approval` 正确流转
- 审批日志落库
- 下载链接有效期生效

---

## 10. fixture 与 utils 建议

### 9.1 fixture 建议文件

- `auth.fixture.ts`
- `project.fixture.ts`
- `brand.fixture.ts`
- `dataset.fixture.ts`
- `questionnaire.fixture.ts`
- `task.fixture.ts`
- `export.fixture.ts`

### 9.2 utils 建议文件

- `downloads.ts`
- `polling.ts`
- `api-client.ts`
- `test-ids.ts`
- `storage.ts`

---

## 11. test tags 建议

- `@smoke`
- `@core`
- `@upload`
- `@analysis`
- `@export`
- `@questionnaire`
- `@restricted`

---

## 12. 后续建议

建议继续产出：

1. `playwright.config.ts` 草案
2. fixture 代码骨架
3. 角色账号准备清单
4. 黄金数据集目录规范
