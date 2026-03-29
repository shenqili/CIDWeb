# 企业级皮肤大数据管理与智能分析平台 演示环境启动说明 v1

## 1. 目标

本文件用于配合：

- [docker-compose.demo.yml](D:\CIDWeb\docker-compose.demo.yml)
- [.env.demo.example](D:\CIDWeb\.env.demo.example)

完成本地 Docker Compose 演示环境准备。

---

## 2. 前置条件

- 已安装 Docker Desktop 或等效 Docker 环境
- 当前仓库根目录为 `D:\CIDWeb`
- 已准备以下目录：
- `frontend/`
- `backend/`
- `storage/raw`
- `storage/intermediate`
- `storage/exports`
- `storage/charts`
- `storage/manifests`
- `storage/audit-attachments`

---

## 3. 环境变量

1. 复制：

`D:\CIDWeb\.env.demo.example` -> `D:\CIDWeb\.env.demo`

2. 按本机需要修改：

- `JWT_SECRET`
- `NEXT_PUBLIC_API_BASE_URL`
- `POSTGRES_PASSWORD`

---

## 4. 启动步骤

1. 创建本地存储目录
2. 准备 `frontend` 与 `backend` 代码目录
3. 复制 `.env.demo.example`
4. 执行：

```powershell
docker compose -f docker-compose.demo.yml up -d
```

5. 检查容器：

- `frontend`
- `api`
- `worker`
- `scheduler`
- `postgres`
- `redis`

---

## 5. 演示建议顺序

1. 登录后台
2. 创建项目并绑定多品牌
3. 上传数据
4. 运行快速分析
5. 运行高级分析
6. 发起高敏导出审批
7. 演示外部匿名问卷
8. 演示历史问卷导入

---

## 6. 当前阶段说明

- 当前为演示环境，不是生产部署方案
- 文件默认保存在宿主机本地目录
- 未来可迁移到对象存储和云端容器平台

