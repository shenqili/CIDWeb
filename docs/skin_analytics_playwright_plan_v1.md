# 企业级皮肤大数据管理与智能分析平台 Playwright 用例清单与测试骨架方案 v1

## 1. 目标

本文件用于把：

- [测试验收方案 v1](D:\CIDWeb\docs\skin_analytics_test_acceptance_plan_v1.md)

进一步落成可执行的浏览器端到端测试计划。

---

## 2. 工具选型

- 推荐工具：`Playwright`

原因：

- 支持 Chromium / Firefox / WebKit
- 支持 `storageState`
- 支持文件上传下载
- 支持网络拦截
- 支持多角色并行测试

---

## 3. 目录结构建议

```text
tests/
  e2e/
    auth/
    projects/
    brands/
    uploads/
    analysis/
    exports/
    questionnaires/
    restricted-analytics/
  fixtures/
  utils/
playwright.config.ts
```

---

## 4. 角色与 storageState

建议预置：

- `super-admin.json`
- `tenant-admin.json`
- `brand-config-admin.json`
- `uploader.json`
- `analyst.json`

---

## 5. 测试数据准备

### 5.1 基础数据

- 一个演示租户
- 两个品牌
- 一个多品牌项目
- 一个已发布数据版本

### 5.2 问卷数据

- 一个公开匿名问卷活动
- 一份历史问卷 Excel
- 一份存在 `RD` 映射冲突的样本

### 5.3 高敏导出数据

- 一条会命中审批流的分析结果

---

## 6. 核心 E2E 用例清单

### 6.1 认证

- 登录成功
- 登录失败
- 首登改密

### 6.2 项目初始化

- 创建项目
- 绑定多个品牌
- 绑定 `VersionBundle`

### 6.3 数据上传

- 标准上传成功
- 字段映射
- 发布版本

### 6.4 主键映射

- `微生态编号` 自动映射
- `RD` 冲突进入人工映射
- 人工映射提交成功

### 6.5 快速分析

- 进入快速分析
- 选择品牌和数据版本
- 运行分析
- 查看结果

### 6.6 高级分析

- 进入高级分析
- 配置变量与参数
- 提交任务
- 查看任务中心

### 6.7 品牌切换

- 切换品牌
- 不兼容变量清空
- 兼容内容保留

### 6.8 派生变量发布

- 发布派生变量
- 生成新版本
- 跳转新版本详情

### 6.9 高敏导出审批

- 创建审批单
- 审批通过
- 下载链接可用
- 审批拒绝
- 审批过期

### 6.10 外部匿名问卷

- 打开外部匿名链接
- 填写问卷
- 提交成功

### 6.11 历史问卷导入

- 上传历史问卷 Excel
- 识别模板
- 执行编号映射
- 完成导入

### 6.12 受限分析空间

- 超级管理员进入
- 执行跨租户聚合分析
- 默认仅输出聚合结果

---

## 7. 推荐 spec 文件命名

- `auth.login.spec.ts`
- `projects.bootstrap.spec.ts`
- `uploads.publish-version.spec.ts`
- `identifier-mapping.manual-confirm.spec.ts`
- `analysis.quick.spec.ts`
- `analysis.advanced.spec.ts`
- `analysis.brand-switch.spec.ts`
- `derived.publish.spec.ts`
- `exports.approval.spec.ts`
- `questionnaires.public-anonymous.spec.ts`
- `questionnaires.import-history.spec.ts`
- `restricted-analytics.aggregate.spec.ts`

---

## 8. 测试骨架建议

### 8.1 公共 fixture

- 登录态装载
- 当前项目上下文
- 当前品牌上下文
- 下载目录

### 8.2 公共 helper

- `loginAs(role)`
- `selectProject(projectName)`
- `selectBrand(brandName)`
- `waitForTaskDone(taskId)`
- `approveExport(requestId)`

### 8.3 公共断言

- 页面标题断言
- 结果摘要卡断言
- 审批状态断言
- 下载文件存在断言

---

## 9. 文件上传与下载测试

### 上传

- 使用 Playwright 文件上传接口
- 验证上传后状态变化

### 下载

- 使用 `page.waitForEvent('download')`
- 保存到测试临时目录
- 校验文件名与大小

---

## 10. 关键风险点

- 多角色状态隔离
- 异步任务超时
- 外部匿名问卷链接失效
- 高敏导出审批状态漂移
- 本地文件目录权限问题

---

## 11. 下一步

建议继续产出：

1. `playwright.config.ts` 草案
2. fixture 目录规范
3. 角色账号准备清单
4. 黄金数据集目录规范

