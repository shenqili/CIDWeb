# CIDWeb

## Demo Startup

Current design and implementation artifacts are in:

- [docs](D:\CIDWeb\docs)

Prepare the local demo environment:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init-demo-env.ps1
Copy-Item .\.env.demo.example .\.env.demo
docker compose -f .\docker-compose.demo.yml up -d
```

Notes:

- The current stage uses local filesystem storage mounted into containers.
- `frontend/` and `backend/` must contain runnable application code.
- Future deployment can migrate to cloud object storage and cloud container runtime without changing the high-level design.
