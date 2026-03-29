# 企业级皮肤大数据管理与智能分析平台 独立问卷模块设计方案 v1

## 1. 文档目标

本文件用于设计一个可独立演示、可后续平台化扩展的问卷模块。

输入依据：

- [PRD v3.1](D:\CIDWeb\docs\skin_analytics_platform_prd_v3_1.md)
- [技术架构与实现方案 v1](D:\CIDWeb\docs\skin_analytics_technical_architecture_v1.md)
- [分析方法与可视化研究 v1](D:\CIDWeb\docs\skin_analytics_analysis_visualization_research_v1.md)

目标：

- 明确问卷模块的功能边界
- 明确技术实现路径
- 明确数据模型
- 明确交互方案
- 参考开源问卷项目的成熟能力

---

## 2. 模块定位

问卷模块不是单纯的“表单录入工具”，而是：

- 问卷模板管理中心
- 题型与逻辑引擎
- 计分引擎
- 问卷结果入库与分析变量生产器

在平台中的位置：

- 可独立作为“问卷配置与问卷结果模块”
- 也可作为品牌配置中心下的子模块

---

## 3. 功能范围

### 3.1 模板管理

- 创建问卷模板
- 版本化管理
- 复制模板
- 项目级复制改写
- 发布/废弃

### 3.2 题型支持

- 单选题
- 多选题
- 下拉题
- 量表题
- 矩阵题
- 文本题
- 数值题
- 日期题
- 文件题

### 3.3 逻辑支持

- 显示逻辑
- 跳题逻辑
- 必答逻辑
- 选项互斥
- 条件分支

### 3.4 计分与派生

- 题目分值
- 反向计分
- 维度分
- 总分
- 分类标签
- 发布为派生变量

### 3.5 结果处理

- 结果入库
- 问卷结果与 `Subject` 绑定
- 缺失题处理
- 跳题冲突识别
- 进入后续分析

### 3.6 发放与采集模式

- 平台内人工录入
- 链接问卷
- 二维码问卷
- 外部匿名填写
- 在线实时答卷
- 导入外部答卷结果
- Excel 批量导入历史答卷结果

---

## 4. 开源参考与吸收策略

### 4.0 对比结论表

| 方案 | 优势 | 局限 | 适合借鉴 |
| --- | --- | --- | --- |
| SurveyJS | React 集成好，题型与逻辑丰富，Schema 成熟 | 商业化边界需要评估，平台级深度集成仍需自定义 | 模板结构、前端渲染、逻辑表达 |
| LimeSurvey | 问卷管理经验丰富，assessment 强 | UI 风格较重，自成系统感强 | 计分、条件逻辑、题型设计 |
| Formbricks | 自托管思路清晰，现代化体验 | 偏调研反馈场景，复杂计分能力相对有限 | 自托管与运营模式 |
| Form.io | Schema 与逻辑计算强 | 更像通用表单引擎，统计分析链路需自补 | 计算型字段、逻辑表达 |

### 4.1 SurveyJS

适合借鉴：

- 题型丰富
- 条件逻辑表达清晰
- JSON Schema 形式成熟
- React 集成较好

适合吸收：

- 模板结构方式
- 前端题目渲染与逻辑表达模式

### 4.2 LimeSurvey

适合借鉴：

- 量表与 assessment 能力
- 条件逻辑成熟
- 问卷管理经验丰富

适合吸收：

- 计分思路
- 条件与跳题配置方式

### 4.3 Formbricks

适合借鉴：

- 自托管思路
- 现代化问卷产品交互
- 轻量调查场景

适合吸收：

- 运营与自托管架构思路
- 结果管理和简洁交互

### 4.4 Form.io

适合借鉴：

- 复杂逻辑
- 计算型字段
- Schema 驱动

适合吸收：

- 逻辑与计算表达
- 后端表单 schema 思路

### 4.5 结论

不建议直接把外部开源问卷系统整体嵌入主平台。更适合的路线是：

- 问卷模块自研
- 题目与逻辑 schema 借鉴 SurveyJS / Form.io
- 计分与 assessment 借鉴 LimeSurvey
- 自托管与演示部署思路参考 Formbricks

---

## 5. 技术方案

### 5.1 前端

- React 问卷渲染器
- 问卷模板编辑器
- 逻辑规则编辑器
- 计分规则编辑器

### 5.2 后端

- 模板服务
- 逻辑校验服务
- 计分服务
- 结果入库服务
- 问卷分发与答卷提交服务
- 历史答卷导入服务

### 5.3 存储

- 问卷模板与版本存数据库
- 问卷逻辑与计分规则以 JSON 存储
- 文件题附件走本地文件存储

### 5.4 部署

- 当前阶段随主平台一起 Docker Compose 部署
- 模块独立 API，但共用主平台身份体系

---

## 6. 数据模型

### 6.1 核心表

- `questionnaire_template`
- `questionnaire_template_version`
- `questionnaire_question`
- `questionnaire_option`
- `questionnaire_response`
- `questionnaire_response_item`
- `questionnaire_scoring_result`

### 6.2 补充说明

#### `questionnaire_response`

记录一份问卷答卷头信息：

- `response_id`
- `project_id`
- `brand_id`
- `dataset_version_id`
- `subject_id`
- `visit_id`
- `template_version_id`
- `status`
- `submitted_at`
- `submission_channel`
- `campaign_id`
- `is_anonymous`

建议状态：

- `draft`
- `submitted`
- `invalid`
- `scored`
- `pending_match`

#### `questionnaire_response_item`

记录单题答案：

- `response_item_id`
- `response_id`
- `question_id`
- `raw_answer_json`
- `normalized_answer_json`
- `is_missing`
- `logic_warning_flag`

#### `questionnaire_scoring_result`

记录计分结果：

- `scoring_result_id`
- `response_id`
- `score_type` (`question/dimension/total/tag`)
- `score_code`
- `score_value`
- `derived_label`

---

## 7. 交互设计

### 7.1 模板编辑页

区块：

- 模板列表
- 题目结构树
- 题目编辑区
- 逻辑区
- 计分区

### 7.2 问卷预览页

区块：

- 题目渲染区
- 页码区
- 条件逻辑提示
- 提交区

适用模式：

- 项目内登录用户填写
- 外部匿名链接填写
- 二维码移动端填写

### 7.3 结果管理页

区块：

- 答卷列表
- 答卷详情
- 计分结果
- 异常项提示

### 7.4 与主平台的连接点

- 项目初始化时绑定问卷模板版本
- 数据导入时识别问卷编号
- 分析结果后可把问卷分值发布成派生变量

### 7.4.1 历史答卷导入页

区块：

- 文件上传区
- 模板匹配区
- 编号映射区
- 异常项提示区

关键动作：

- 上传历史答卷 Excel
- 识别模板版本
- 执行 `RD / RD- / 微生态编号` 映射
- 生成问卷答卷导入批次

### 7.5 问卷发放与回收页

区块：

- 发放方式选择
- 问卷链接区
- 二维码区
- 答卷回收统计
- 提醒与截止时间配置

---

## 8. 关键业务规则

### 8.1 计分规则

- 由超级管理员和品牌配置管理员维护基线规则
- 项目允许复制后改写
- 改写后的规则仅作用于当前项目

### 8.2 跳题逻辑

- 若应跳过但有答案，标记逻辑冲突
- 若应作答但缺失，标记缺失异常
- 当前阶段建议警告优先，不一律阻断

### 8.3 采集模式规则

- 平台内人工录入默认绑定登录用户上下文
- 链接问卷和二维码问卷支持外部受访者填写
- 外部答卷若无法映射 `subject_id`，进入待匹配状态
- 外部匿名答卷通过 `campaignToken` 和可选一次性访问令牌控制
- 在线实时答卷与历史批量导入答卷必须进入同一计分与质检流程

### 8.4 多选题

- 原始答案保留数组
- 标准化后可拆成多列派生变量

### 8.5 派生变量发布

- 总分、维度分、标签可进入 `DerivedVariableSet`
- 发布后生成新 `DatasetVersion`

---

## 9. 分阶段实现

### Phase 1

- 模板管理
- 常见题型
- 基础逻辑
- 基础计分
- 结果入库

### Phase 2

- 矩阵题
- 文件题
- 跳题校验增强
- 维度分与总分派生

### Phase 3

- 模板市场
- 问卷跨项目复用
- 更复杂逻辑表达

---

## 10. 当前建议

当前阶段建议：

- 不直接引入完整第三方问卷系统
- 保持主平台一体化体验
- 内部使用 Schema 驱动的问卷模块
- 保留未来替换或兼容 SurveyJS 式渲染器的空间
