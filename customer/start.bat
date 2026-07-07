@echo off
setlocal EnableExtensions
cd /d "%~dp0\.."
set "ROOT_DIR=%CD%"

call "%ROOT_DIR%\customer\scripts\load-config.bat"

docker info >nul 2>&1
if errorlevel 1 (
  echo.
  echo Docker is not running. Open Docker Desktop, wait until it is ready, then run this again.
  echo.
  pause
  exit /b 1
)

if not exist "%ROOT_DIR%\.env" (
  copy /Y "%ROOT_DIR%\.env.customer.example" "%ROOT_DIR%\.env" >nul
)

curl -sf "%HEALTH_URL%" >nul 2>&1
if not errorlevel 1 (
  echo IPCAS is already running.
  start "" "%APP_URL%"
  pause
  exit /b 0
)

echo.
echo Starting IPCAS...
echo.

call "%ROOT_DIR%\customer\scripts\compose.bat" up -d --build
if errorlevel 1 (
  echo Docker compose failed.
  pause
  exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%ROOT_DIR%\customer\scripts\wait-for-stack.ps1"
if errorlevel 1 (
  echo IPCAS did not become ready in time.
  pause
  exit /b 1
)

start "" "%APP_URL%"
echo.
echo IPCAS is running at %APP_URL%
echo.
pause
endlocal
