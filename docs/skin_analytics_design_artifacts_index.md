# 企业级皮肤大数据管理与智能分析平台 设计产物索引

## 已完成文档

- [PRD v3.1](D:\CIDWeb\docs\skin_analytics_platform_prd_v3_1.md)
- [分阶段开发与验收执行方案 v1](D:\CIDWeb\docs\skin_analytics_phased_delivery_execution_plan_v1.md)
- [阶段 0 执行与验收报告 v1](D:\CIDWeb\docs\skin_analytics_phase_0_execution_report_v1.md)
- [技术架构与实现方案 v1](D:\CIDWeb\docs\skin_analytics_technical_architecture_v1.md)
- [ERD v1](D:\CIDWeb\docs\skin_analytics_erd_v1.md)
- [API 设计 v1](D:\CIDWeb\docs\skin_analytics_api_design_v1.md)
- [OpenAPI v1](D:\CIDWeb\docs\skin_analytics_openapi_v1.yaml)
- [OpenAPI v1.1](D:\CIDWeb\docs\skin_analytics_openapi_v1_1.yaml)
- [页面级原型说明 v1](D:\CIDWeb\docs\skin_analytics_page_prototype_v1.md)
- [页面线框级说明 v1](D:\CIDWeb\docs\skin_analytics_page_wireframes_v1.md)
- [页面状态图与关键页面高保真说明 v1](D:\CIDWeb\docs\skin_analytics_page_states_hifi_notes_v1.md)
- [全量数据明细浏览模块设计 v1](D:\CIDWeb\docs\skin_analytics_data_explorer_design_v1.md)
- [测试验收方案 v1](D:\CIDWeb\docs\skin_analytics_test_acceptance_plan_v1.md)
- [Playwright 用例清单与测试骨架方案 v1](D:\CIDWeb\docs\skin_analytics_playwright_plan_v1.md)
- [Playwright Fixture 与用例骨架方案 v1](D:\CIDWeb\docs\skin_analytics_playwright_fixtures_tests_v1.md)
- [分析方法与可视化专业研究 v1](D:\CIDWeb\docs\skin_analytics_analysis_visualization_research_v1.md)
- [独立问卷模块设计方案 v1](D:\CIDWeb\docs\skin_analytics_questionnaire_module_design_v1.md)
- [源文件追溯矩阵 v1](D:\CIDWeb\docs\skin_analytics_source_traceability_v1.md)
- [Docker Compose 演示环境设计 v1](D:\CIDWeb\docs\skin_analytics_docker_compose_demo_design_v1.md)
- [演示环境启动说明 v1](D:\CIDWeb\docs\skin_analytics_demo_environment_setup_v1.md)
- [docker-compose.demo.yml](D:\CIDWeb\docker-compose.demo.yml)
- [PostgreSQL DDL v1](D:\CIDWeb\docs\skin_analytics_postgresql_ddl_v1.sql)
- [实现文档复审报告 v1](D:\CIDWeb\docs\skin_analytics_implementation_docs_review_v1.md)
- [实现文档复审报告 v2](D:\CIDWeb\docs\skin_analytics_implementation_docs_review_v2.md)
- [详细设计复审报告 v1](D:\CIDWeb\docs\skin_analytics_detailed_design_review_v1.md)
- [最终交付报告 v1](D:\CIDWeb\docs\skin_analytics_final_delivery_report_v1.md)
- [阶段 0 执行与验收报告 v1](D:\CIDWeb\docs\skin_analytics_phase_0_execution_report_v1.md)
- [阶段 0/1 执行报告 v1](D:\CIDWeb\docs\skin_analytics_phase_0_1_execution_report_v1.md)
- [阶段 1 执行与验收报告 v1](D:\CIDWeb\docs\skin_analytics_phase_1_execution_report_v1.md)
- [阶段 1 当前任务清单 v1](D:\CIDWeb\docs\skin_analytics_phase_1_current_task_list_v1.md)
- [阶段 2 当前任务清单 v1](D:\CIDWeb\docs\skin_analytics_phase_2_current_task_list_v1.md)
- [阶段 3 当前任务清单 v1](D:\CIDWeb\docs\skin_analytics_phase_3_current_task_list_v1.md)
- [阶段 4 当前任务清单 v1](D:\CIDWeb\docs\skin_analytics_phase_4_current_task_list_v1.md)
- [阶段 5 当前任务清单 v1](D:\CIDWeb\docs\skin_analytics_phase_5_current_task_list_v1.md)
- [阶段 6 当前任务清单 v1](D:\CIDWeb\docs\skin_analytics_phase_6_current_task_list_v1.md)
- [分阶段测试总策略 v1](D:\CIDWeb\docs\skin_analytics_phase_test_strategy_v1.md)
- [阶段 0/1 执行报告 v1](D:\CIDWeb\docs\skin_analytics_stage_0_1_execution_report_v1.md)

## 配置与测试骨架

- [.env.demo.example](D:\CIDWeb\.env.demo.example)
- [playwright.config.ts](D:\CIDWeb\playwright.config.ts)
- [auth.fixture.ts](D:\CIDWeb\tests\fixtures\auth.fixture.ts)
- [project.fixture.ts](D:\CIDWeb\tests\fixtures\project.fixture.ts)
- [brand.fixture.ts](D:\CIDWeb\tests\fixtures\brand.fixture.ts)
- [dataset.fixture.ts](D:\CIDWeb\tests\fixtures\dataset.fixture.ts)
- [questionnaire.fixture.ts](D:\CIDWeb\tests\fixtures\questionnaire.fixture.ts)
- [task.fixture.ts](D:\CIDWeb\tests\fixtures\task.fixture.ts)
- [export.fixture.ts](D:\CIDWeb\tests\fixtures\export.fixture.ts)

## 已确认关键边界

- 问卷模块支持外部填写
- 问卷模块支持在线实时答卷
- 问卷模块支持 Excel 批量导入历史答卷结果
- 当前阶段采用本地文件存储
- 当前阶段后端采用 Docker / Docker Compose 演示部署

## 参考文档

- [SPSSAU 可视化界面参考附录](D:\CIDWeb\docs\skin_analytics_spssau_visual_reference.md)
- [PRD v3 多维复审报告](D:\CIDWeb\docs\skin_analytics_platform_prd_v3_review_report.md)
- [数据源对齐说明](D:\CIDWeb\docs\skin_analytics_source_alignment_notes.md)
- [设计文档跨文档复审报告 v1](D:\CIDWeb\docs\skin_analytics_design_docs_review_report_v1.md)
- [设计包复核报告 v1](D:\CIDWeb\docs\skin_analytics_design_package_review_v1.md)
- [分析/问卷专项复审结论 v1](D:\CIDWeb\docs\skin_analytics_research_modules_review_report_v1.md)
