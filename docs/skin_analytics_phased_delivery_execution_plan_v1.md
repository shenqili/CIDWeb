# 企业级皮肤大数据管理与智能分析平台 分阶段开发与验收执行方案 v1

## 1. 文档目标

本文件用于指导后续团队按阶段推进：

- 开发
- 联调
- 测试
- 验收
- 修复

适用对象：

- 产品经理
- 架构师
- 前端开发
- 后端开发
- 数据/分析开发
- QA
- DevOps

关联文档：

- [PRD v3.1](D:\CIDWeb\docs\skin_analytics_platform_prd_v3_1.md)
- [技术架构与实现方案 v1](D:\CIDWeb\docs\skin_analytics_technical_architecture_v1.md)
- [ERD v1](D:\CIDWeb\docs\skin_analytics_erd_v1.md)
- [PostgreSQL DDL v1](D:\CIDWeb\docs\skin_analytics_postgresql_ddl_v1.sql)
- [API 设计 v1](D:\CIDWeb\docs\skin_analytics_api_design_v1.md)
- [OpenAPI v1.1](D:\CIDWeb\docs\skin_analytics_openapi_v1_1.yaml)
- [页面级原型说明 v1](D:\CIDWeb\docs\skin_analytics_page_prototype_v1.md)
- [页面状态图与关键页面高保真说明 v1](D:\CIDWeb\docs\skin_analytics_page_states_hifi_notes_v1.md)
- [测试验收方案 v1](D:\CIDWeb\docs\skin_analytics_test_acceptance_plan_v1.md)
- [Playwright Fixture 与用例骨架方案 v1](D:\CIDWeb\docs\skin_analytics_playwright_fixtures_tests_v1.md)
- [分阶段 E2E 策略 v1](D:\CIDWeb\docs\skin_analytics_phase_e2e_strategy_v1.md)
- [分析方法与可视化专业研究 v1](D:\CIDWeb\docs\skin_analytics_analysis_visualization_research_v1.md)
- [独立问卷模块设计方案 v1](D:\CIDWeb\docs\skin_analytics_questionnaire_module_design_v1.md)
- [源文件追溯矩阵 v1](D:\CIDWeb\docs\skin_analytics_source_traceability_v1.md)
- [Docker Compose 演示环境设计 v1](D:\CIDWeb\docs\skin_analytics_docker_compose_demo_design_v1.md)
- [演示环境启动说明 v1](D:\CIDWeb\docs\skin_analytics_demo_environment_setup_v1.md)
- [最终交付报告 v1](D:\CIDWeb\docs\skin_analytics_final_delivery_report_v1.md)

---

## 1.1 总控使用方式

本文件应作为后续团队推进的“总控导航文件”，使用方式如下：

- 每个阶段开始前，先阅读本文件对应阶段章节
- 按本文件中的“阶段必读文档”进入详细设计文档
- 开发、测试、验收、修复都回到本文件确认是否偏离阶段边界
- 若发生需求变更或设计更新，应优先回填到本文件的阶段映射

### 1.2 文档分类

为避免后续团队找文档混乱，现有文档按用途划分如下：

#### 产品与需求基线

- [PRD v3.1](D:\CIDWeb\docs\skin_analytics_platform_prd_v3_1.md)
- [源文件追溯矩阵 v1](D:\CIDWeb\docs\skin_analytics_source_traceability_v1.md)

#### 技术与数据设计

- [技术架构与实现方案 v1](D:\CIDWeb\docs\skin_analytics_technical_architecture_v1.md)
- [ERD v1](D:\CIDWeb\docs\skin_analytics_erd_v1.md)
- [PostgreSQL DDL v1](D:\CIDWeb\docs\skin_analytics_postgresql_ddl_v1.sql)
- [API 设计 v1](D:\CIDWeb\docs\skin_analytics_api_design_v1.md)
- [OpenAPI v1.1](D:\CIDWeb\docs\skin_analytics_openapi_v1_1.yaml)

#### 页面与交互设计

- [页面级原型说明 v1](D:\CIDWeb\docs\skin_analytics_page_prototype_v1.md)
- [页面线框级说明 v1](D:\CIDWeb\docs\skin_analytics_page_wireframes_v1.md)
- [页面状态图与关键页面高保真说明 v1](D:\CIDWeb\docs\skin_analytics_page_states_hifi_notes_v1.md)
- [SPSSAU 可视化界面参考附录](D:\CIDWeb\docs\skin_analytics_spssau_visual_reference.md)

#### 测试与验收

- [测试验收方案 v1](D:\CIDWeb\docs\skin_analytics_test_acceptance_plan_v1.md)
- [Playwright 用例清单与测试骨架方案 v1](D:\CIDWeb\docs\skin_analytics_playwright_plan_v1.md)
- [Playwright Fixture 与用例骨架方案 v1](D:\CIDWeb\docs\skin_analytics_playwright_fixtures_tests_v1.md)
- [分阶段 E2E 策略 v1](D:\CIDWeb\docs\skin_analytics_phase_e2e_strategy_v1.md)
- [分阶段测试总策略 v1](D:\CIDWeb\docs\skin_analytics_phase_test_strategy_v1.md)

#### 专业研究与专项模块

- [分析方法与可视化专业研究 v1](D:\CIDWeb\docs\skin_analytics_analysis_visualization_research_v1.md)
- [独立问卷模块设计方案 v1](D:\CIDWeb\docs\skin_analytics_questionnaire_module_design_v1.md)

#### 环境与部署

- [Docker Compose 演示环境设计 v1](D:\CIDWeb\docs\skin_analytics_docker_compose_demo_design_v1.md)
- [演示环境启动说明 v1](D:\CIDWeb\docs\skin_analytics_demo_environment_setup_v1.md)
- [docker-compose.demo.yml](D:\CIDWeb\docker-compose.demo.yml)
- [.env.demo.example](D:\CIDWeb\.env.demo.example)

#### 复审与总览

- [最终交付报告 v1](D:\CIDWeb\docs\skin_analytics_final_delivery_report_v1.md)
- [设计产物索引](D:\CIDWeb\docs\skin_analytics_design_artifacts_index.md)

---

## 2. 执行原则

- 先底座，后主链路，再扩能力
- 每一阶段必须有可演示产物
- 每一阶段必须有可回归测试范围
- 每一阶段结束前必须完成缺陷回修
- 不跨阶段堆积高优先级缺陷
- 文档、接口、数据库、页面、测试必须同步演进

---

## 3. 团队角色与职责

### 3.1 产品与设计

- 维护阶段范围
- 决定是否通过阶段验收
- 管理需求变更

### 3.2 架构与后端

- 落数据库、API、任务流、权限、审批流
- 保证版本绑定与隔离规则一致

### 3.3 前端

- 落页面框架、状态流、工作台、问卷页、结果页
- 与 OpenAPI 对齐

### 3.4 数据/分析开发

- 落统计方法
- 落图表导出
- 落派生变量回写

### 3.5 QA

- 维护阶段测试范围
- 冒烟、回归、E2E
- 出具验收结论

### 3.6 DevOps

- 维护 Docker Compose 演示环境
- 环境一致性、日志、目录、启动脚本

### 3.7 角色必读文档

#### 产品经理

- [PRD v3.1](D:\CIDWeb\docs\skin_analytics_platform_prd_v3_1.md)
- [分阶段开发与验收执行方案 v1](D:\CIDWeb\docs\skin_analytics_phased_delivery_execution_plan_v1.md)
- [最终交付报告 v1](D:\CIDWeb\docs\skin_analytics_final_delivery_report_v1.md)
- [阶段 1 当前任务清单 v1](D:\CIDWeb\docs\skin_analytics_phase_1_current_task_list_v1.md)
- [阶段 2 当前任务清单 v1](D:\CIDWeb\docs\skin_analytics_phase_2_current_task_list_v1.md)
- [阶段 3 当前任务清单 v1](D:\CIDWeb\docs\skin_analytics_phase_3_current_task_list_v1.md)
- [阶段 4 当前任务清单 v1](D:\CIDWeb\docs\skin_analytics_phase_4_current_task_list_v1.md)
- [阶段 5 当前任务清单 v1](D:\CIDWeb\docs\skin_analytics_phase_5_current_task_list_v1.md)
- [阶段 6 当前任务清单 v1](D:\CIDWeb\docs\skin_analytics_phase_6_current_task_list_v1.md)

#### 架构师 / 后端

- [技术架构与实现方案 v1](D:\CIDWeb\docs\skin_analytics_technical_architecture_v1.md)
- [ERD v1](D:\CIDWeb\docs\skin_analytics_erd_v1.md)
- [PostgreSQL DDL v1](D:\CIDWeb\docs\skin_analytics_postgresql_ddl_v1.sql)
- [API 设计 v1](D:\CIDWeb\docs\skin_analytics_api_design_v1.md)
- [OpenAPI v1.1](D:\CIDWeb\docs\skin_analytics_openapi_v1_1.yaml)

#### 前端 / 设计

- [页面级原型说明 v1](D:\CIDWeb\docs\skin_analytics_page_prototype_v1.md)
- [页面线框级说明 v1](D:\CIDWeb\docs\skin_analytics_page_wireframes_v1.md)
- [页面状态图与关键页面高保真说明 v1](D:\CIDWeb\docs\skin_analytics_page_states_hifi_notes_v1.md)
- [SPSSAU 可视化界面参考附录](D:\CIDWeb\docs\skin_analytics_spssau_visual_reference.md)

#### QA

- [测试验收方案 v1](D:\CIDWeb\docs\skin_analytics_test_acceptance_plan_v1.md)
- [Playwright 用例清单与测试骨架方案 v1](D:\CIDWeb\docs\skin_analytics_playwright_plan_v1.md)
- [Playwright Fixture 与用例骨架方案 v1](D:\CIDWeb\docs\skin_analytics_playwright_fixtures_tests_v1.md)
- [分阶段测试总策略 v1](D:\CIDWeb\docs\skin_analytics_phase_test_strategy_v1.md)

#### 数据 / 分析开发

- [分析方法与可视化专业研究 v1](D:\CIDWeb\docs\skin_analytics_analysis_visualization_research_v1.md)
- [源文件追溯矩阵 v1](D:\CIDWeb\docs\skin_analytics_source_traceability_v1.md)
- [独立问卷模块设计方案 v1](D:\CIDWeb\docs\skin_analytics_questionnaire_module_design_v1.md)

#### DevOps

- [Docker Compose 演示环境设计 v1](D:\CIDWeb\docs\skin_analytics_docker_compose_demo_design_v1.md)
- [演示环境启动说明 v1](D:\CIDWeb\docs\skin_analytics_demo_environment_setup_v1.md)
- [docker-compose.demo.yml](D:\CIDWeb\docker-compose.demo.yml)
- [.env.demo.example](D:\CIDWeb\.env.demo.example)

---

## 4. 阶段总览

### 4.0 阶段与文档映射总表

| 阶段 | 核心目标 | 阶段必读文档 | 主要交付参考 |
| --- | --- | --- | --- |
| 阶段 0 | 环境与脚手架基线 | [技术架构与实现方案 v1](D:\CIDWeb\docs\skin_analytics_technical_architecture_v1.md), [Docker Compose 演示环境设计 v1](D:\CIDWeb\docs\skin_analytics_docker_compose_demo_design_v1.md), [演示环境启动说明 v1](D:\CIDWeb\docs\skin_analytics_demo_environment_setup_v1.md), [分阶段 E2E 策略 v1](D:\CIDWeb\docs\skin_analytics_phase_e2e_strategy_v1.md), [分阶段测试总策略 v1](D:\CIDWeb\docs\skin_analytics_phase_test_strategy_v1.md) | [docker-compose.demo.yml](D:\CIDWeb\docker-compose.demo.yml), [.env.demo.example](D:\CIDWeb\.env.demo.example) |
| 阶段 1 | 数据底座 | [PRD v3.1](D:\CIDWeb\docs\skin_analytics_platform_prd_v3_1.md), [ERD v1](D:\CIDWeb\docs\skin_analytics_erd_v1.md), [PostgreSQL DDL v1](D:\CIDWeb\docs\skin_analytics_postgresql_ddl_v1.sql), [源文件追溯矩阵 v1](D:\CIDWeb\docs\skin_analytics_source_traceability_v1.md), [分阶段 E2E 策略 v1](D:\CIDWeb\docs\skin_analytics_phase_e2e_strategy_v1.md), [分阶段测试总策略 v1](D:\CIDWeb\docs\skin_analytics_phase_test_strategy_v1.md), [阶段 1 当前任务清单 v1](D:\CIDWeb\docs\skin_analytics_phase_1_current_task_list_v1.md) | [API 设计 v1](D:\CIDWeb\docs\skin_analytics_api_design_v1.md), [OpenAPI v1.1](D:\CIDWeb\docs\skin_analytics_openapi_v1_1.yaml) |
| 阶段 2 | 分析主链路 | [PRD v3.1](D:\CIDWeb\docs\skin_analytics_platform_prd_v3_1.md), [分析方法与可视化专业研究 v1](D:\CIDWeb\docs\skin_analytics_analysis_visualization_research_v1.md), [页面级原型说明 v1](D:\CIDWeb\docs\skin_analytics_page_prototype_v1.md), [全量数据明细浏览模块设计 v1](D:\CIDWeb\docs\skin_analytics_data_explorer_design_v1.md), [分阶段 E2E 策略 v1](D:\CIDWeb\docs\skin_analytics_phase_e2e_strategy_v1.md), [分阶段测试总策略 v1](D:\CIDWeb\docs\skin_analytics_phase_test_strategy_v1.md), [阶段 2 当前任务清单 v1](D:\CIDWeb\docs\skin_analytics_phase_2_current_task_list_v1.md) | [页面线框级说明 v1](D:\CIDWeb\docs\skin_analytics_page_wireframes_v1.md), [页面状态图与关键页面高保真说明 v1](D:\CIDWeb\docs\skin_analytics_page_states_hifi_notes_v1.md) |
| 阶段 3 | 问卷与审批链路 | [独立问卷模块设计方案 v1](D:\CIDWeb\docs\skin_analytics_questionnaire_module_design_v1.md), [PRD v3.1](D:\CIDWeb\docs\skin_analytics_platform_prd_v3_1.md), [OpenAPI v1.1](D:\CIDWeb\docs\skin_analytics_openapi_v1_1.yaml), [分阶段 E2E 策略 v1](D:\CIDWeb\docs\skin_analytics_phase_e2e_strategy_v1.md), [分阶段测试总策略 v1](D:\CIDWeb\docs\skin_analytics_phase_test_strategy_v1.md), [阶段 3 当前任务清单 v1](D:\CIDWeb\docs\skin_analytics_phase_3_current_task_list_v1.md) | [页面级原型说明 v1](D:\CIDWeb\docs\skin_analytics_page_prototype_v1.md), [Playwright Fixture 与用例骨架方案 v1](D:\CIDWeb\docs\skin_analytics_playwright_fixtures_tests_v1.md) |
| 阶段 4 | 高级分析能力 | [分析方法与可视化专业研究 v1](D:\CIDWeb\docs\skin_analytics_analysis_visualization_research_v1.md), [PRD v3.1](D:\CIDWeb\docs\skin_analytics_platform_prd_v3_1.md), [分阶段 E2E 策略 v1](D:\CIDWeb\docs\skin_analytics_phase_e2e_strategy_v1.md), [分阶段测试总策略 v1](D:\CIDWeb\docs\skin_analytics_phase_test_strategy_v1.md), [阶段 4 当前任务清单 v1](D:\CIDWeb\docs\skin_analytics_phase_4_current_task_list_v1.md) | [页面状态图与关键页面高保真说明 v1](D:\CIDWeb\docs\skin_analytics_page_states_hifi_notes_v1.md), [OpenAPI v1.1](D:\CIDWeb\docs\skin_analytics_openapi_v1_1.yaml) |
| 阶段 5 | 平台治理与受限空间 | [PRD v3.1](D:\CIDWeb\docs\skin_analytics_platform_prd_v3_1.md), [技术架构与实现方案 v1](D:\CIDWeb\docs\skin_analytics_technical_architecture_v1.md), [Docker Compose 演示环境设计 v1](D:\CIDWeb\docs\skin_analytics_docker_compose_demo_design_v1.md), [分阶段 E2E 策略 v1](D:\CIDWeb\docs\skin_analytics_phase_e2e_strategy_v1.md), [分阶段测试总策略 v1](D:\CIDWeb\docs\skin_analytics_phase_test_strategy_v1.md), [阶段 5 当前任务清单 v1](D:\CIDWeb\docs\skin_analytics_phase_5_current_task_list_v1.md) | [OpenAPI v1.1](D:\CIDWeb\docs\skin_analytics_openapi_v1_1.yaml), [测试验收方案 v1](D:\CIDWeb\docs\skin_analytics_test_acceptance_plan_v1.md) |
| 阶段 6 | 自动化与演示收口 | [测试验收方案 v1](D:\CIDWeb\docs\skin_analytics_test_acceptance_plan_v1.md), [Playwright 用例清单与测试骨架方案 v1](D:\CIDWeb\docs\skin_analytics_playwright_plan_v1.md), [Playwright Fixture 与用例骨架方案 v1](D:\CIDWeb\docs\skin_analytics_playwright_fixtures_tests_v1.md), [分阶段 E2E 策略 v1](D:\CIDWeb\docs\skin_analytics_phase_e2e_strategy_v1.md), [分阶段测试总策略 v1](D:\CIDWeb\docs\skin_analytics_phase_test_strategy_v1.md), [阶段 6 当前任务清单 v1](D:\CIDWeb\docs\skin_analytics_phase_6_current_task_list_v1.md), [演示环境启动说明 v1](D:\CIDWeb\docs\skin_analytics_demo_environment_setup_v1.md) | [docker-compose.demo.yml](D:\CIDWeb\docker-compose.demo.yml), [最终交付报告 v1](D:\CIDWeb\docs\skin_analytics_final_delivery_report_v1.md) |

### 阶段 0：项目基线与脚手架

目标：

- 让所有团队成员在同一个仓库、同一套文档和同一套环境约定下工作

包含：

- 仓库结构
- `docker-compose.demo.yml`
- `.env.demo.example`
- `playwright.config.ts`
- 基础目录结构
- 文档索引

阶段交付物：

- 可拉起的演示环境空壳
- 初始化说明

阶段验收标准：

- 团队成员可以按文档成功启动环境
- 目录结构与设计文档一致

回修重点：

- 环境变量错误
- 挂载目录错误
- README/文档不一致

### 阶段 1：数据底座

目标：

- 让平台能安全地接入数据、识别主键、生成版本

包含：

- 多租户和用户权限基础
- 项目管理
- 品牌绑定
- 品牌用户权限配置
- 品牌指标配置确认
- 品牌配置版本发布
- `VersionBundle`
- 数据集
- 上传向导
- 主键映射
- 数据版本与 lineage

不包含：

- 完整统计分析
- 问卷发放
- 高敏导出审批

阶段交付物：

- 数据接入 API
- 基础数据库表
- 上传和数据版本页面
- 品牌配置与版本绑定页面
- 品牌用户授权与品牌范围控制

阶段测试：

- 品牌用户仅可见授权品牌
- 品牌指标配置确认与版本发布
- 上传标准文件
- 主键冲突处理
- 数据版本发布
- 多品牌项目切换
- 上传数据与品牌绑定一致性校验

阶段验收标准：

- 可以完成“项目初始化 -> 品牌用户授权 -> 品牌指标配置确认 -> 上传 -> 发布版本”
- `微生态编号 / RD / RD-` 映射链条可用
- 所有入库数据都必须绑定到正确的品牌与 `VersionBundle`

回修重点：

- 品牌范围权限错误
- 品牌配置版本错误
- 主键冲突
- 映射错误
- 版本状态错误

补充说明：

- 阶段 1 验收报告中的非阻断回修项不留在本阶段悬空，必须显式转入后续阶段闭环。
- 多角色负向权限回归转入阶段 2。
- 跨品牌混合分析限制转入阶段 5。
- 导入失败链路浏览器回归转入阶段 6。
- 正式认证与授权体系替换 `demo auth` 已由阶段 1 `v2` 报告闭环，不再计入后续阶段待办。

### 阶段 2：分析主链路

目标：

- 让普通用户能完成第一次完整分析闭环

包含：

- 全量数据明细浏览 / `Data Explorer`
- 快速分析
- 高级分析基础壳子
- 频数分析与样本画像
- 描述统计
- 差异分析
- 相关分析
- 基础回归
- 结果详情页
- 任务中心
- 派生变量发布

不包含：

- GLM
- 因子分析
- 聚类分析
- 问卷外部发放

阶段交付物：

- `Data Explorer` 页面
- 分析工作台
- 结果页
- 任务中心
- 派生变量发布链路

阶段测试：

- `Data Explorer` 浏览、筛选、图表预览
- `Data Explorer` 中的品牌切换与权限隔离
- 未授权品牌访问拦截与品牌切换后的上下文重校验
- 快速分析主链路
- 高级分析主链路
- 品牌切换
- 派生变量发布为新版本

阶段验收标准：

- 可以完成“发布版本 -> Data Explorer 浏览与筛选 -> 分析 -> 查看结果 -> 发布派生变量”
- `Data Explorer` 可完成明细浏览、字段筛选、基础图表查看
- 普通用户在阶段 2 分析主链路中无法带入未授权品牌上下文，品牌切换后上下文与数据版本会重新校验
- 主图、主表、结果摘要可导出

回修重点：

- 数据浏览上下文错误
- 明细筛选与图表联动错误
- 方法推荐错误
- 任务状态错误
- 结果页上下文错误

### 阶段 3：问卷模块与审批链路

目标：

- 让问卷模块与主平台数据链路打通，并让高敏导出审批可用

包含：

- 问卷模板管理
- 问卷逻辑与计分
- 项目级复制改写
- 外部匿名填写
- 在线实时答卷
- 历史问卷批量导入
- 高敏导出审批

阶段交付物：

- 问卷模板页
- 问卷预览与答卷页
- 问卷发放页
- 问卷历史导入页
- 高敏导出审批流

阶段测试：

- 匿名问卷主链路
- 问卷历史导入
- 反向题、多选题、跳题逻辑
- 审批通过/拒绝/过期

阶段验收标准：

- 问卷结果能入库、计分、映射、发布派生变量
- 高敏导出必须经审批后才能下载

回修重点：

- 问卷逻辑错误
- 计分错误
- 匿名问卷失效
- 审批状态流错误

### 阶段 4：高级分析能力

目标：

- 打开面向研究和专家用户的高级能力

包含：

- GLM
- 因子分析
- 聚类分析
- 问卷列联分析增强
- 图表工作台增强
- 高级诊断图

阶段交付物：

- 高级方法面板
- 载荷图、森林图、Q-Q 图、残差热图

阶段测试：

- 高级方法黄金数据集
- 自动推荐与手动覆盖
- 派生变量从高级方法发布

阶段验收标准：

- 高级方法结果可复现
- 图表导出与结果说明一致

回修重点：

- 方法数值偏差
- 执行快照缺失
- 图表导出不一致

### 阶段 5：平台治理与受限空间

目标：

- 完成企业级治理闭环

包含：

- 平台级受限分析空间
- 跨租户聚合分析
- 保留策略
- RPO/RTO
- 日志与清理任务

阶段交付物：

- 受限空间页面
- 聚合分析链路
- 清理与保留策略配置

阶段测试：

- 超级管理员受限空间
- 聚合结果限制
- 普通用户跨品牌混合分析请求被拒绝并留痕
- 过期导出清理
- 审计追溯

阶段验收标准：

- 普通用户无法进入受限分析空间
- 受限空间默认仅输出聚合结果
- 跨品牌混合分析限制在界面、API 与审计留痕三层闭环

回修重点：

- 越权访问
- 聚合结果泄漏明细
- 审计缺失

### 阶段 6：自动化与演示收口

目标：

- 保证可稳定演示、可持续回归

包含：

- Playwright 冒烟
- 核心 E2E
- 演示账号
- 演示数据
- 演示脚本

阶段交付物：

- Playwright fixture
- E2E 套件
- 演示步骤文档

阶段测试：

- Smoke
- Core
- Full
- 导入失败链路浏览器回归，覆盖空主键、非法字段映射、重复发布幂等、XLSX 浏览器上传专项

阶段验收标准：

- 核心主链路可以自动化回归
- Docker 演示环境可稳定跑通
- `full` 套件已覆盖阶段 1 验收报告转入的失败路径回归项

回修重点：

- 环境不稳定
- 测试波动
- 演示脚本断链

---

## 5. 每阶段统一执行模板

每个阶段统一按以下节奏执行：

1. 冻结阶段范围
2. 拆任务
3. 开发
4. 联调
5. 测试
6. 验收
7. 缺陷回修
8. 阶段关闭

### 5.1 阶段入口条件

每个阶段开始前，至少满足：

- 上一阶段 `P0` 缺陷已清零
- 上一阶段核心交付物已冻结
- 当前阶段必读文档已更新到最新版本
- 当前阶段负责人与测试范围已明确

### 5.2 阶段退出条件

每个阶段结束前，至少满足：

- 当前阶段目标已达成
- 当前阶段交付物已落库到仓库与文档索引
- 当前阶段 `P0` 缺陷为 0
- 当前阶段 `P1` 缺陷已评估并决定清零或转移
- QA 已出具阶段验收结论

---

## 6. 每阶段必须产出的东西

### 开发侧

- 代码
- 数据库变更
- 接口变更
- 页面变更

### 文档侧

- 接口更新
- 测试用例更新
- 演示说明更新

### 测试侧

- 冒烟结果
- 缺陷清单
- 阶段验收结论

---

## 7. 缺陷优先级处理规则

### P0

- 阻断主链路
- 阶段不得关闭

### P1

- 影响阶段目标
- 原则上阶段关闭前清零

### P2

- 不阻断阶段目标
- 可进入下一阶段修复池

### P3

- 体验优化项
- 可统一收口

---

## 8. 测试分层策略

### Smoke

- 登录
- 项目初始化
- 上传
- 快速分析

### Core

- 高级分析
- 派生变量发布
- 问卷匿名填写
- 问卷历史导入
- 高敏导出审批

### Full

- 受限分析空间
- 高级统计方法
- 数据清理与恢复

---

## 9. 阶段间依赖

- 阶段 1 是所有后续阶段前置
- 阶段 2 依赖阶段 1
- 阶段 3 依赖阶段 1 和阶段 2
- 阶段 4 依赖阶段 2
- 阶段 5 依赖阶段 2、3、4
- 阶段 6 贯穿全程，但以阶段 2 之后为重点

---

## 10. 当前建议的开发顺序

1. 阶段 0
2. 阶段 1
3. 阶段 2
4. 阶段 3
5. 阶段 4
6. 阶段 5
7. 阶段 6

---

## 11. 使用方式

后续团队推进时，建议每周或每迭代都引用本文件：

- 先确认当前处于哪个阶段
- 只做该阶段范围内的内容
- 测试与验收按该阶段的标准来
- 修复优先处理该阶段的 `P0/P1`
