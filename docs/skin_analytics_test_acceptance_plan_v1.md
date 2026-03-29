# 企业级皮肤大数据管理与智能分析平台测试与验收计划 v1

## 1. 本轮验收范围

本轮验收覆盖阶段 1 core 闭环：

1. 品牌用户权限控制
2. 品牌配置 / 版本最小链路
3. 字段映射 / 主键映射
4. 数据版本发布
5. 阶段 1 `core` 级浏览器 E2E

## 2. 执行环境

- 项目目录：`D:\CIDWeb`
- 前端：`http://127.0.0.1:3000`
- 后端：`http://127.0.0.1:8000`
- 样本文件：`D:\CIDWeb\tmp_input\phase1-core-ascii.csv`

## 3. 验收用例

### Smoke

- 首页可访问
- 健康检查接口可访问
- 工作台 Shell 可访问

### Core

- 品牌管理员切换到 `brand-bdf` 后，仅可见授权品牌，并可发布最小品牌配置版本
- 超级管理员可完成数据集创建、上传文件、字段映射、主键映射、数据版本发布

## 4. 执行记录

执行命令：

```powershell
npx playwright test tests/e2e/smoke --reporter=list
npx playwright test tests/e2e/core --reporter=list
npx playwright test tests/e2e/smoke tests/e2e/core
```

执行结果：

- `smoke`：4 / 4 通过
- `core`：2 / 2 通过
- 总计：6 / 6 通过

HTML 报告：

- [playwright-report/index.html](D:\CIDWeb\playwright-report\index.html)

截图证据：

- [phase1-brands-browser-acceptance.png](D:\CIDWeb\docs\evidence\phase1-brands-browser-acceptance.png)
- [phase1-data-browser-acceptance.png](D:\CIDWeb\docs\evidence\phase1-data-browser-acceptance.png)

## 5. 验收结论

本轮验收结果支持阶段 1 core 闭环。

说明：

- 已覆盖真实浏览器链路，不再停留在接口级或占位页面级验证。
- 成功路径已闭环，失败路径仍建议在下一轮补充。
