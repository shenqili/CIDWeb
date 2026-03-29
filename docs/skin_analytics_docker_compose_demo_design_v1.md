# 企业级皮肤大数据管理与智能分析平台 Docker Compose 演示环境设计 v1

## 1. 目标

本文件用于说明：

- [docker-compose.demo.yml](D:\CIDWeb\docker-compose.demo.yml)

所定义的演示环境结构、服务职责、卷挂载、本地目录规划和未来云迁移注意点。

---

## 2. 演示环境目标

当前阶段的目标不是生产级高可用，而是：

- 一键启动可演示环境
- 覆盖前端、后端、数据库、缓存、异步任务
- 支撑本地文件存储
- 支撑问卷、分析、导出和审批主链路

---

## 3. 容器拓扑

### `frontend`

职责：

- Next.js 前端页面渲染
- 浏览器端交互

### `api`

职责：

- FastAPI 主应用
- 认证、项目、配置、上传、分析编排、审批 API

### `worker`

职责：

- 异步统计分析
- 图表导出
- 派生变量发布后台任务

### `scheduler`

职责：

- 周期任务
- 清理过期导出
- 清理中间文件
- 审批过期扫描

### `postgres`

职责：

- 业务事务数据库

### `redis`

职责：

- 缓存
- 异步任务队列

### `virus-scan`

职责：

- 文件扫描

---

## 4. 卷挂载与本地目录

### 宿主机目录

建议在项目根目录存在：

- `./storage/raw`
- `./storage/intermediate`
- `./storage/exports`
- `./storage/charts`
- `./storage/manifests`
- `./storage/audit-attachments`

### 容器挂载

- `api` 挂载 `./storage:/storage`
- `worker` 挂载 `./storage:/storage`
- `scheduler` 挂载 `./storage:/storage`

### 原则

- 所有文件统一走 `/storage`
- 本地演示时直接查看宿主机目录即可验证结果

---

## 5. 启动顺序

推荐顺序：

1. `postgres`
2. `redis`
3. `api`
4. `worker`
5. `scheduler`
6. `frontend`

`docker-compose.demo.yml` 已通过 `depends_on` 和 `healthcheck` 表达基本顺序。

---

## 6. 关键环境变量

### API / Worker / Scheduler

- `DATABASE_URL`
- `REDIS_URL`
- `STORAGE_ROOT`
- `RAW_STORAGE_ROOT`
- `INTERMEDIATE_STORAGE_ROOT`
- `EXPORT_STORAGE_ROOT`
- `CHART_STORAGE_ROOT`
- `MANIFEST_STORAGE_ROOT`

### Frontend

- `NEXT_PUBLIC_API_BASE_URL`

---

## 7. 演示环境建议准备的数据

- 预置一个演示租户
- 预置两个品牌
- 预置一个多品牌项目
- 预置一份已发布数据版本
- 预置一个高敏导出审批演示场景
- 预置一个外部匿名问卷活动

---

## 8. 演示建议流程

1. 启动 `docker-compose.demo.yml`
2. 登录平台
3. 查看项目和品牌绑定
4. 上传样例数据
5. 运行快速分析
6. 查看结果和图表
7. 发起高敏导出审批
8. 演示外部匿名问卷填写

---

## 9. 当前阶段限制

- `frontend` / `api` / `worker` 目录需要后续代码实现
- 当前 Compose 文件主要用于设计与后续脚手架落地
- 不等价于生产部署

---

## 10. 未来云迁移注意点

- 文件层从本地 `/storage` 迁移到对象存储
- `postgres` / `redis` 可替换为托管服务
- `worker` / `scheduler` 可迁移到云端容器平台
- 当前目录规则保持不变，仅底层实现替换

