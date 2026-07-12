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

if not exist "%ROOT_DIR%\customer\ipcas.config" (
  if exist "%ROOT_DIR%\customer\ipcas.config.example" (
    copy /Y "%ROOT_DIR%\customer\ipcas.config.example" "%ROOT_DIR%\customer\ipcas.config" >nul
    echo Created customer\ipcas.config from example.
    call "%ROOT_DIR%\customer\scripts\load-config.bat"
  )
)

echo.
echo Building and starting IPCAS. First run may take several minutes...
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
echo IPCAS is installed and running.
echo Open in browser: %APP_URL%
echo Demo login: +10000000001 / devpass123
echo.
echo To stop:   double-click customer\stop.bat
echo To update: double-click customer\update.bat
echo.
pause
endlocal
