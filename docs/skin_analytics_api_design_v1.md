# 企业级皮肤大数据管理与智能分析平台 API 设计 v1

## 1. 文档目标

本文件用于承接：

- [PRD v3.1](D:\CIDWeb\docs\skin_analytics_platform_prd_v3_1.md)
- [技术架构与实现方案 v1](D:\CIDWeb\docs\skin_analytics_technical_architecture_v1.md)
- [ERD v1](D:\CIDWeb\docs\skin_analytics_erd_v1.md)

目标：

- 明确核心资源分组
- 定义主要 REST API
- 明确异步任务、审批流、版本绑定和鉴权约定
- 支撑浏览器端主要交互流程

---

## 2. 总体约定

### 2.1 API 风格

- 风格：REST
- 基础路径：`/api/v1`
- 默认格式：`application/json`
- 文件上传采用 `multipart/form-data`
- 文件下载采用流式响应或短时效链接

### 2.2 鉴权

- 建议：`JWT + Refresh Token`
- Token 内至少包含：
- `userId`
- `tenantId`
- `roles`
- `projectScopes`
- `brandScopes`
- `isSuperAdmin`

### 2.3 版本绑定约定

所有分析相关请求必须显式带上：

- `projectId`
- `brandId`
- `versionBundleId`
- `datasetVersionId`

禁止后端隐式取“项目最新配置”或“项目最新数据版本”。

### 2.4 幂等

以下接口必须支持 `idempotencyKey`：

- 创建分析任务
- 创建导出任务
- 发布派生变量
- 创建高敏导出审批单

### 2.5 错误码建议

- `400` 参数错误
- `401` 未认证
- `403` 未授权
- `404` 资源不存在
- `409` 版本冲突 / 主键映射冲突
- `422` 业务校验失败
- `429` 队列限流
- `500` 系统错误

---

## 3. 资源分组

### 3.1 基础资源

- `auth`
- `tenants`
- `projects`
- `brands-config`
- `questionnaires`
- `datasets`
- `subjects-visits`

### 3.2 业务资源

- `analysis`
- `charts-exports`
- `tasks`
- `audit-approvals`

### 3.3 平台级资源

- `system-admin`
- `restricted-analytics`

---

## 4. 核心接口

### 4.1 `auth`

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`
- `POST /api/v1/auth/refresh`

### 4.2 `tenants`

- `GET /api/v1/tenants`
- `POST /api/v1/tenants`
- `GET /api/v1/tenants/{tenantId}`
- `PATCH /api/v1/tenants/{tenantId}`
- `GET /api/v1/tenants/{tenantId}/users`
- `POST /api/v1/tenants/{tenantId}/users`
- `PATCH /api/v1/tenants/{tenantId}/users/{userId}`

### 4.3 `projects`

- `GET /api/v1/projects`
- `POST /api/v1/projects`
- `GET /api/v1/projects/{projectId}`
- `PATCH /api/v1/projects/{projectId}`
- `GET /api/v1/projects/{projectId}/members`
- `POST /api/v1/projects/{projectId}/members`
- `GET /api/v1/projects/{projectId}/brand-bindings`
- `PUT /api/v1/projects/{projectId}/brand-bindings`
- `GET /api/v1/projects/{projectId}/version-bundles`
- `POST /api/v1/projects/{projectId}/version-bundles`

### 4.4 `brands-config`

- `GET /api/v1/brands`
- `POST /api/v1/brands`
- `GET /api/v1/brands/{brandId}`
- `GET /api/v1/brands/{brandId}/config-versions`
- `POST /api/v1/brands/{brandId}/config-versions`
- `PATCH /api/v1/brands/{brandId}/config-versions/{versionId}`
- `POST /api/v1/brands/{brandId}/config-versions/{versionId}/publish`
- `GET /api/v1/metric-catalogs`
- `GET /api/v1/metric-catalogs/{catalogId}/versions`
- `GET /api/v1/questionnaire-templates`
- `GET /api/v1/questionnaire-templates/{templateId}/versions`
- `POST /api/v1/version-bundles`
- `GET /api/v1/version-bundles/{bundleId}`

### 4.4.1 `questionnaires`

- `GET /api/v1/questionnaire-templates`
- `POST /api/v1/questionnaire-templates`
- `GET /api/v1/questionnaire-templates/{templateId}`
- `GET /api/v1/questionnaire-templates/{templateId}/versions`
- `POST /api/v1/questionnaire-templates/{templateId}/versions`
- `POST /api/v1/questionnaire-templates/{templateId}/versions/{versionId}/publish`
- `POST /api/v1/questionnaire-campaigns`
- `GET /api/v1/questionnaire-campaigns/{campaignId}`
- `POST /api/v1/questionnaire-campaigns/{campaignId}/publish`
- `GET /api/v1/public/questionnaires/{campaignToken}`
- `POST /api/v1/public/questionnaires/{campaignToken}/submit`
- `POST /api/v1/questionnaire-responses`
- `POST /api/v1/questionnaire-response-imports`
- `GET /api/v1/questionnaire-response-imports/{importId}`
- `GET /api/v1/questionnaire-responses/{responseId}`
- `GET /api/v1/questionnaire-responses/{responseId}/items`
- `GET /api/v1/questionnaire-responses/{responseId}/scores`
- `POST /api/v1/questionnaire-responses/{responseId}/score`

### 4.5 `datasets`

- `GET /api/v1/projects/{projectId}/datasets`
- `POST /api/v1/projects/{projectId}/datasets`
- `GET /api/v1/datasets/{datasetId}`
- `POST /api/v1/datasets/{datasetId}/uploads`
- `GET /api/v1/uploads/{uploadId}`
- `POST /api/v1/uploads/{uploadId}/parse`
- `POST /api/v1/uploads/{uploadId}/mapping`
- `POST /api/v1/uploads/{uploadId}/preprocess`
- `POST /api/v1/uploads/{uploadId}/publish-version`
- `GET /api/v1/datasets/{datasetId}/versions`
- `GET /api/v1/dataset-versions/{datasetVersionId}`
- `GET /api/v1/dataset-versions/{datasetVersionId}/profile`
- `GET /api/v1/dataset-versions/{datasetVersionId}/browse-filters`
- `POST /api/v1/dataset-versions/{datasetVersionId}/browse/query`
- `POST /api/v1/dataset-versions/{datasetVersionId}/chart-previews`
- `POST /api/v1/dataset-versions/{datasetVersionId}/freeze`
- `POST /api/v1/dataset-versions/{datasetVersionId}/archive`
- `GET /api/v1/dataset-versions/{datasetVersionId}/diff/{targetVersionId}`

### 4.5.1 `data-explorer`

- `GET /api/v1/projects/{projectId}/data-explorer/context`
- `GET /api/v1/projects/{projectId}/data-explorer/fields`
- `POST /api/v1/projects/{projectId}/data-explorer/query`
- `POST /api/v1/projects/{projectId}/data-explorer/charts/preview`
- `POST /api/v1/projects/{projectId}/data-explorer/selection-to-analysis`

### 4.6 `subjects-visits`

- `GET /api/v1/dataset-versions/{datasetVersionId}/subjects`
- `GET /api/v1/subjects/{subjectId}`
- `GET /api/v1/subjects/{subjectId}/identifiers`
- `POST /api/v1/subjects/{subjectId}/identifiers`
- `POST /api/v1/identifier-mappings/manual-confirm`
- `GET /api/v1/visits/{visitId}`

### 4.7 `analysis`

- `GET /api/v1/projects/{projectId}/analysis-templates`
- `POST /api/v1/projects/{projectId}/analysis-templates`
- `POST /api/v1/analysis-jobs`
- `GET /api/v1/analysis-jobs/{jobId}`
- `POST /api/v1/analysis-jobs/{jobId}/rerun`
- `POST /api/v1/analysis-jobs/{jobId}/cancel`
- `GET /api/v1/analysis-jobs/{jobId}/result`
- `GET /api/v1/analysis-jobs/{jobId}/manifest`
- `GET /api/v1/analysis-jobs/{jobId}/derived-variable-set`
- `POST /api/v1/derived-variable-sets/{setId}/publish`

### 4.8 `charts-exports`

- `GET /api/v1/analysis-results/{resultId}/charts`
- `POST /api/v1/analysis-results/{resultId}/charts`
- `PATCH /api/v1/charts/{chartId}`
- `POST /api/v1/charts/{chartId}/render`
- `POST /api/v1/exports`
- `GET /api/v1/exports/{exportId}`
- `GET /api/v1/exports/{exportId}/download`

### 4.9 `tasks`

- `GET /api/v1/tasks`
- `GET /api/v1/tasks/{taskId}`
- `POST /api/v1/tasks/{taskId}/retry`
- `POST /api/v1/tasks/{taskId}/cancel`

### 4.10 `audit-approvals`

- `GET /api/v1/audit-logs`
- `GET /api/v1/export-approval-requests`
- `POST /api/v1/export-approval-requests`
- `GET /api/v1/export-approval-requests/{requestId}`
- `POST /api/v1/export-approval-requests/{requestId}/approve`
- `POST /api/v1/export-approval-requests/{requestId}/reject`

### 4.11 `restricted-analytics`

- `POST /api/v1/restricted-analytics/jobs`
- `GET /api/v1/restricted-analytics/jobs/{jobId}`
- `GET /api/v1/restricted-analytics/jobs/{jobId}/result`
- `POST /api/v1/restricted-analytics/exports`
- `POST /api/v1/restricted-analytics/exports/{exportId}/request-detail-export`

---

## 5. 关键资源结构

### 5.1 `Project`

```json
{
  "id": "proj_001",
  "tenantId": "tenant_001",
  "name": "BDF 皮肤研究项目",
  "status": "active",
  "allowedBrandIds": ["brand_bdf", "brand_clarins"],
  "defaultImportMode": "batch",
  "highSensitivityExportPolicy": "approval_required"
}
```

### 5.2 `VersionBundle`

```json
{
  "id": "vb_001",
  "projectId": "proj_001",
  "brandId": "brand_bdf",
  "brandConfigVersionId": "bcv_003",
  "metricCatalogVersionId": "mcv_007",
  "questionnaireTemplateVersionId": "qtv_002",
  "status": "published"
}
```

### 5.3 `DatasetVersion`

```json
{
  "id": "dsv_001",
  "datasetId": "ds_001",
  "projectId": "proj_001",
  "brandId": "brand_bdf",
  "parentVersionId": null,
  "importBatchId": "batch_001",
  "status": "published",
  "rowCount": 5116,
  "columnCount": 1401
}
```

### 5.3.1 `DatasetVersionProfile`

```json
{
  "datasetVersionId": "dsv_001",
  "projectId": "proj_001",
  "brandId": "brand_bdf",
  "datasetId": "ds_001",
  "datasetName": "BDF 2026 主数据集",
  "versionNo": "v1.3",
  "rowCount": 5116,
  "columnCount": 1401,
  "publishedAt": "2026-03-29T09:00:00Z",
  "fieldSummary": {
    "analyzableFieldCount": 780,
    "dimensionFieldCount": 54,
    "highSensitivityFieldCount": 12
  },
  "sampleSummary": {
    "missingPrimaryKeyRate": 0.0,
    "visitCount": 5116
  }
}
```

### 5.3.2 `DataExplorerQuery` 请求

```json
{
  "projectId": "proj_001",
  "brandId": "brand_bdf",
  "datasetId": "ds_001",
  "datasetVersionId": "dsv_001",
  "page": 1,
  "pageSize": 50,
  "sort": [
    {
      "field": "visit_date",
      "direction": "desc"
    }
  ],
  "visibleFields": ["subject_id", "rd", "city_group", "MX18_黑素_面颊"],
  "filters": [
    {
      "field": "city_group",
      "operator": "in",
      "value": ["上海", "北京"]
    },
    {
      "field": "age",
      "operator": "between",
      "value": [18, 35]
    }
  ]
}
```

### 5.3.3 `DataExplorerQuery` 响应

```json
{
  "datasetVersionId": "dsv_001",
  "page": 1,
  "pageSize": 50,
  "totalRows": 642,
  "returnedRows": 50,
  "visibleFields": ["subject_id", "rd", "city_group", "MX18_黑素_面颊"],
  "rows": [
    {
      "subject_id": "sub_001",
      "rd": "RD0001",
      "city_group": "上海",
      "MX18_黑素_面颊": 23.4
    }
  ],
  "summary": {
    "filteredRowCount": 642,
    "missingRate": 0.013
  }
}
```

### 5.3.4 `ChartPreview` 响应

```json
{
  "datasetVersionId": "dsv_001",
  "charts": [
    {
      "chartType": "histogram",
      "field": "MX18_黑素_面颊",
      "title": "黑素分布",
      "spec": {
        "x": [10, 20, 30],
        "y": [32, 88, 15]
      }
    }
  ]
}
```

### 5.4 `AnalysisJob` 请求

```json
{
  "projectId": "proj_001",
  "brandId": "brand_bdf",
  "versionBundleId": "vb_001",
  "datasetVersionId": "dsv_001",
  "analysisType": "anova",
  "mode": "quick",
  "cohortRuleId": "cohort_001",
  "variables": {
    "groupVar": "年龄分组",
    "targetVars": ["MX18_黑素_面颊"]
  },
  "options": {
    "postHoc": "tukey",
    "alpha": 0.05
  },
  "idempotencyKey": "job-anova-proj001-001"
}
```

### 5.4.1 `QuestionnaireResponse` 请求

```json
{
  "projectId": "proj_001",
  "brandId": "brand_bdf",
  "templateVersionId": "qtv_002",
  "subjectId": "sub_001",
  "visitId": "visit_001",
  "answers": [
    {
      "questionCode": "Q1",
      "rawAnswer": "油性"
    },
    {
      "questionCode": "Q2",
      "rawAnswer": ["成分", "功效"]
    }
  ]
}
```

### 5.5 `AnalysisJob` 响应

```json
{
  "id": "aj_001",
  "status": "queued",
  "taskId": "task_001",
  "executionManifestId": "manifest_001",
  "resultId": null
}
```

### 5.6 `ExecutionManifest`

```json
{
  "id": "manifest_001",
  "tenantId": "tenant_001",
  "projectId": "proj_001",
  "brandId": "brand_bdf",
  "versionBundleId": "vb_001",
  "datasetVersionId": "dsv_001",
  "datasetVersionHash": "sha256:xxx",
  "analysisTemplateVersion": "atv_003",
  "engineVersion": "analysis-engine-1.0.0",
  "libraryLock": {
    "pandas": "2.2.3",
    "scipy": "1.13.1",
    "statsmodels": "0.14.2"
  },
  "randomSeed": 42,
  "timezone": "Asia/Shanghai",
  "manifestHash": "sha256:yyy"
}
```

### 5.7 `ExportApprovalRequest`

```json
{
  "id": "ear_001",
  "exportId": "exp_001",
  "tenantId": "tenant_001",
  "projectId": "proj_001",
  "requestedBy": "user_001",
  "approverId": "tenant_admin_001",
  "status": "pending_approval",
  "reason": "论文投稿使用",
  "expiresAt": "2026-04-01T12:00:00Z"
}
```

### 5.8 `QuestionnaireCampaign`

```json
{
  "id": "qc_001",
  "projectId": "proj_001",
  "brandId": "brand_bdf",
  "templateVersionId": "qtv_002",
  "accessMode": "public_anonymous",
  "campaignToken": "qtoken_xxx",
  "status": "published",
  "expiresAt": "2026-04-30T23:59:59Z"
}
```

### 5.9 `QuestionnaireResponseImport`

```json
{
  "id": "qri_001",
  "projectId": "proj_001",
  "brandId": "brand_bdf",
  "templateVersionId": "qtv_002",
  "datasetVersionId": "dsv_001",
  "status": "queued",
  "sourceFileName": "history_questionnaire.xlsx"
}
```

### 5.10 `DatasetVersionProfile`

```json
{
  "datasetVersionId": "dsv_001",
  "projectId": "proj_001",
  "brandId": "brand_bdf",
  "datasetId": "ds_001",
  "sampleCount": 5116,
  "fieldCount": 1129,
  "missingRateSummary": {
    "highMissingFieldCount": 23,
    "fullyPopulatedFieldCount": 804
  }
}
```

### 5.11 `BrowseQueryRequest`

```json
{
  "projectId": "proj_001",
  "brandId": "brand_bdf",
  "datasetVersionId": "dsv_001",
  "selectedFields": ["RD", "年龄分组", "MX18_黑素_面颊"],
  "filters": [
    {
      "field": "年龄分组",
      "operator": "in",
      "value": ["25-30", "31-35"]
    }
  ],
  "sort": {
    "field": "RD",
    "direction": "asc"
  },
  "page": 1,
  "pageSize": 50
}
```

### 5.12 `BrowseQueryResponse`

```json
{
  "querySnapshotId": "browse_001",
  "summary": {
    "sampleCount": 1268,
    "fieldCount": 3
  },
  "columns": [
    {
      "field": "RD",
      "label": "RD",
      "dataType": "string"
    }
  ],
  "rows": [
    {
      "RD": "RD0001",
      "年龄分组": "25-30",
      "MX18_黑素_面颊": 132.4
    }
  ],
  "page": 1,
  "pageSize": 50,
  "totalPages": 26
}
```

---

## 6. 异步任务与审批流

### 6.1 通用任务状态

- `draft`
- `queued`
- `running`
- `partial_success`
- `succeeded`
- `failed`
- `cancelled`
- `expired`

### 6.2 任务接口

- `POST /api/v1/analysis-jobs`
- `GET /api/v1/tasks/{taskId}`
- `POST /api/v1/tasks/{taskId}/retry`
- `POST /api/v1/tasks/{taskId}/cancel`

### 6.3 高敏导出审批接口

- `POST /api/v1/export-approval-requests`
- `POST /api/v1/export-approval-requests/{requestId}/approve`
- `POST /api/v1/export-approval-requests/{requestId}/reject`

审批状态：

- `pending_approval`
- `approved`
- `rejected`
- `expired`

### 6.4 派生变量发布接口

- `GET /api/v1/analysis-jobs/{jobId}/derived-variable-set`
- `POST /api/v1/derived-variable-sets/{setId}/publish`

建议请求：

```json
{
  "publishMode": "new_dataset_version",
  "datasetNameSuffix": "derived-20260328",
  "selectedVariables": ["factor_score_1", "cluster_label"]
}
```

---

## 7. 浏览器端关键流程

### 7.1 项目初始化

1. 前端加载项目详情
2. 拉取品牌列表和可发布 `VersionBundle`
3. 提交项目品牌绑定
4. 返回项目初始化完成状态

### 7.2 上传与发布数据版本

1. 前端上传文件到 `uploads`
2. 调用解析接口
3. 获取字段映射建议
4. 提交映射和预处理规则
5. 发布为 `DatasetVersion`

补充约定：

- 上传接口返回 `uploadId / checksum / tempStoragePath`
- 上传响应不得直接暴露宿主机真实目录

### 7.2.2 数据浏览与 Data Explorer

1. 前端先选择 `project + brand + datasetVersion`
2. 拉取 `DatasetVersionProfile` 和 `browse-filters`
3. 提交结构化浏览查询
4. 返回概览卡、分页明细和查询快照
5. 图表预览接口根据当前查询快照返回聚合结果
6. 当前筛选条件可带入快速分析或高级分析

### 7.2.1 问卷答卷提交

1. 前端加载问卷模板版本
2. 根据逻辑规则渲染题目
3. 提交答卷
4. 后端校验跳题逻辑和必答项
5. 生成答卷记录与计分结果
6. 如命中派生规则，可进入派生变量发布流程

### 7.3 快速分析

1. 前端先选择 `project + brand + datasetVersion`
2. 拉取当前品牌下可分析变量
3. 提交快速分析请求
4. 轮询任务状态
5. 成功后跳结果详情页

### 7.4 品牌切换

1. 前端切换品牌
2. 拉取新的 `VersionBundle`
3. 重新校验当前变量、筛选规则、模板
4. 清空不兼容对象
5. 刷新页面上下文

### 7.5 派生变量发布

1. 分析结果页请求 `DerivedVariableSet`
2. 用户选择要发布的变量
3. 提交 `publish`
4. 后端生成新 `DatasetVersion`
5. 前端跳转新版本详情

### 7.6 高敏导出

1. 用户发起导出
2. 若命中高敏策略，创建审批单
3. 前端展示“待审批”
4. 审批通过后生成签名下载链接
5. 前端显示可下载状态

### 7.7 外部匿名问卷填写

1. 用户通过外部链接或二维码打开问卷页
2. 前端根据 `campaignToken` 获取问卷模板版本
3. 填写并实时提交或最终提交答卷
4. 后端创建 `questionnaire_response`
5. 若无法映射 `subject_id`，状态进入 `pending_match`

### 7.8 历史问卷批量导入

1. 项目内用户上传历史问卷 Excel
2. 后端识别模板版本并创建导入任务
3. 执行 `RD / RD- / 微生态编号` 映射
4. 成功入库问卷答卷和计分结果
5. 失败项进入异常清单

补充约定：

- 普通导出可直接流式下载
- 高敏导出仅返回可控的下载元数据，不直接暴露底层文件路径

---

## 8. 设计约束

- 普通用户请求必须同时校验 `tenant + project + brand`
- 超级管理员访问 `restricted-analytics` 必须额外校验 `isSuperAdmin=true`
- 高敏导出下载必须校验审批单状态
- 创建任务、创建导出、发布派生变量都要求 `idempotencyKey`
- 不允许后端隐式取“项目当前最新版本”代替请求入参

---

## 9. 下一步

建议后续继续产出：

1. OpenAPI 草案
2. 错误码表
3. 分页、排序、筛选规范
4. 上传 / 下载 / 审批状态回调协议
