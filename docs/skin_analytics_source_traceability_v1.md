# 企业级皮肤大数据管理与智能分析平台 源文件追溯矩阵 v1

## 1. 目标

本文件用于把最初的 3 份源文件与当前设计文档逐条对齐，确认：

- 原始数据指标是否被系统设计覆盖
- 原始统计方法是否被平台方法设计覆盖
- 原始功能诉求是否被 PRD 与技术方案覆盖

源文件：

- `各家指标(1).xlsx`
- `alldata_260204(1).xlsx`
- `各统计方法(1).docx`

已使用的本地副本：

- `C:\Users\Ryan Shen\tmp_prd_input\vendor_metrics.xlsx`
- `C:\Users\Ryan Shen\tmp_prd_input\alldata_260204.xlsx`
- `C:\Users\Ryan Shen\tmp_prd_input\stat_methods.docx`

---

## 2. `各家指标(1).xlsx` 对齐

### 已确认事实

- 不同品牌的指标集合不同
- 不同品牌的问卷字段集合不同
- 同一仪器在不同品牌下支持的测量点不同

### 当前设计对应

- [PRD v3.1 - 品牌/项目指标配置](D:\CIDWeb\docs\skin_analytics_platform_prd_v3_1.md#L462)
- [PRD v3.1 - 统一指标目录与字段映射](D:\CIDWeb\docs\skin_analytics_platform_prd_v3_1.md#L487)
- [PRD v3.1 - VersionBundle](D:\CIDWeb\docs\skin_analytics_platform_prd_v3_1.md#L631)
- [ERD - `brand_config_version / metric_alias / version_bundle`](D:\CIDWeb\docs\skin_analytics_erd_v1.md)

### 结论

- 已覆盖品牌级指标差异
- 已覆盖部位/测量点差异
- 已覆盖问卷模板与指标模板分版本绑定

---

## 3. `alldata_260204(1).xlsx` 对齐

### 已确认事实

- 主表约 `7320` 行、`1401` 列
- 包含：
  基础人口学
  面部/头部微生态
  面部仪器指标
  医生评估
  头皮仪器指标
  图像量化指标
  问卷字段

### 当前设计对应

- [PRD v3.1 - 主键映射与多源整合](D:\CIDWeb\docs\skin_analytics_platform_prd_v3_1.md#L557)
- [PRD v3.1 - 数据版本](D:\CIDWeb\docs\skin_analytics_platform_prd_v3_1.md#L653)
- [技术架构 - 数据导入流](D:\CIDWeb\docs\skin_analytics_technical_architecture_v1.md#L237)
- [ERD - `subject / subject_identifier / visit_record / dataset_version`](D:\CIDWeb\docs\skin_analytics_erd_v1.md)

### 特别结论

- 当前主表里更稳定的外部唯一编号是 `微生态编号`
- `RD` 与 `RD-问卷编号` 应进入映射关系，而不是直接当唯一主键

### 结论

- 已覆盖宽表治理
- 已覆盖主键映射
- 已覆盖批次/版本设计
- 已覆盖问卷与仪器的统一分析底座

---

## 4. `各统计方法(1).docx` 对齐

### 文档中已确认的方法

- 差异分析
- 相关分析
- 多因素分析（GLM）
- 因子分析
- 聚类分析
- 问卷列联分析

### 当前设计对应

- [PRD v3.1 - 频数分析与样本画像](D:\CIDWeb\docs\skin_analytics_platform_prd_v3_1.md#L1464)
- [PRD v3.1 - 差异分析](D:\CIDWeb\docs\skin_analytics_platform_prd_v3_1.md#L1521)
- [PRD v3.1 - 相关分析](D:\CIDWeb\docs\skin_analytics_platform_prd_v3_1.md#L1581)
- [PRD v3.1 - 回归分析](D:\CIDWeb\docs\skin_analytics_platform_prd_v3_1.md#L1602)
- [PRD v3.1 - 多因素分析](D:\CIDWeb\docs\skin_analytics_platform_prd_v3_1.md#L1633)
- [PRD v3.1 - 因子分析与聚类分析](D:\CIDWeb\docs\skin_analytics_platform_prd_v3_1.md#L1659)
- [PRD v3.1 - 问卷列联分析](D:\CIDWeb\docs\skin_analytics_platform_prd_v3_1.md#L1685)

### 可视化对应

- [散点图、热图、箱线图、误差线图、簇状图、P-P / Q-Q 图参考](D:\CIDWeb\docs\skin_analytics_spssau_visual_reference.md)
- [图表规范](D:\CIDWeb\docs\skin_analytics_platform_prd_v3_1.md#L1730)
- [图表工作台结构](D:\CIDWeb\docs\skin_analytics_platform_prd_v3_1.md#L1787)

### 结论

- 原文档中的统计方法已基本覆盖到当前 PRD
- 结果表达和图形方法也已覆盖到当前平台设计

---

## 5. 与最初功能诉求的对齐

### 已覆盖

- 多租户
- 多品牌项目
- 多用户数据隔离
- 上传分组条件
- 数据上传与预处理
- 描述性统计
- 差异性分析
- 相关性分析
- 回归分析
- 图表导出
- 结果追溯与下载
- 高敏导出审批

### 新增增强

- 频数分析与样本画像
- GLM
- 因子分析
- 聚类分析
- 问卷模块
- 派生变量回写
- 平台级受限分析空间

---

## 6. 当前仍需后续设计细化的内容

这些不是缺失，而是已进入下一阶段设计：

- API 细节和 OpenAPI
- 页面高保真原型
- 统计方法黄金数据集
- Docker Compose 演示环境
- 问卷模块实现细节

---

## 7. 结论

截至当前版本：

- 原始品牌指标文件已进入品牌配置与版本设计
- 原始总表已进入数据模型与主键映射设计
- 原始统计方法文档已进入分析方法与图表方法设计
- 原始功能诉求已基本进入 `PRD v3.1`

整体判断：

- 当前设计已经与原始数据、原始统计方法、原始功能诉求形成较完整闭环

