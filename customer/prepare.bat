@echo off
setlocal EnableExtensions
cd /d "%~dp0\.."
set "ROOT_DIR=%CD%"

call "%ROOT_DIR%\customer\scripts\load-config.bat"

where docker >nul 2>&1
if errorlevel 1 (
  echo.
  echo Docker is not installed. Install Docker Desktop from https://www.docker.com/products/docker-desktop/
  echo.
  pause
  exit /b 1
)

docker info >nul 2>&1
if errorlevel 1 (
  echo.
  echo Docker is not running. Open Docker Desktop, wait until it is ready, then run this again.
  echo.
  pause
  exit /b 1
)

if not exist "%ROOT_DIR%\.env" (
  if not exist "%ROOT_DIR%\.env.customer.example" (
    echo Missing .env.customer.example
    pause
    exit /b 1
  )
  copy /Y "%ROOT_DIR%\.env.customer.example" "%ROOT_DIR%\.env" >nul
  echo Created .env from .env.customer.example
)

echo.
echo Preparing IPCAS for demo (download images + build). This may take 10-20 minutes.
echo Run this once before the customer meeting while you have a stable internet connection.
echo.

call "%ROOT_DIR%\customer\scripts\compose.bat" pull
if errorlevel 1 (
  echo Warning: some image pulls failed. Build will try to fetch missing images.
)

call "%ROOT_DIR%\customer\scripts\compose.bat" build
if errorlevel 1 (
  echo Docker build failed.
  pause
  exit /b 1
)

echo.
echo IPCAS images are ready.
echo On demo day, double-click customer\start.bat (or install.bat on a fresh PC).
echo.
pause
endlocal
