param(
  [string]$Url = $env:HEALTH_URL,
  [int]$MaxAttempts = [int]$env:WAIT_MAX_ATTEMPTS,
  [int]$IntervalSec = [int]$env:WAIT_INTERVAL_SEC
)

if (-not $Url) { $Url = "http://localhost:8080/api/schema/" }
if (-not $MaxAttempts -or $MaxAttempts -le 0) { $MaxAttempts = 90 }
if (-not $IntervalSec -or $IntervalSec -le 0) { $IntervalSec = 2 }

for ($attempt = 1; $attempt -le $MaxAttempts; $attempt++) {
  try {
    Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5 | Out-Null
    Write-Host "IPCAS is ready."
    exit 0
  } catch {
    Write-Host "Waiting for IPCAS... ($attempt/$MaxAttempts)"
    Start-Sleep -Seconds $IntervalSec
  }
}

Write-Error "Timed out waiting for IPCAS at $Url"
exit 1
