$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$dirs = @(
  "storage",
  "storage/raw",
  "storage/intermediate",
  "storage/exports",
  "storage/charts",
  "storage/manifests",
  "storage/audit-attachments",
  "backend",
  "frontend"
)

foreach ($dir in $dirs) {
  $path = Join-Path $root $dir
  if (-not (Test-Path $path)) {
    New-Item -ItemType Directory -Path $path -Force | Out-Null
    Write-Host "Created $path"
  } else {
    Write-Host "Exists   $path"
  }
}

Write-Host ""
Write-Host "Demo directories are ready."
Write-Host "Next steps:"
Write-Host "1. Copy .env.demo.example to .env.demo"
Write-Host "2. Ensure frontend/ and backend/ contain runnable code"
Write-Host "3. Run: docker compose -f docker-compose.demo.yml up -d"

