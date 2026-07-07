@echo off
setlocal EnableExtensions
cd /d "%~dp0\.."
set "ROOT_DIR=%CD%"

call "%ROOT_DIR%\customer\scripts\load-config.bat"

docker info >nul 2>&1
if errorlevel 1 (
  echo Docker is not running. Open Docker Desktop first.
  pause
  exit /b 1
)

where git >nul 2>&1
if errorlevel 1 (
  echo Git is not installed. Install Git, then try again.
  pause
  exit /b 1
)

if not exist "%ROOT_DIR%\.git" (
  echo This folder is not a Git repository.
  echo Clone the project first, then run update.
  pause
  exit /b 1
)

if not exist "%ROOT_DIR%\.env" (
  copy /Y "%ROOT_DIR%\.env.customer.example" "%ROOT_DIR%\.env" >nul
)

echo.
echo Pulling latest code (%GIT_REMOTE%/%GIT_BRANCH%)...
git -C "%ROOT_DIR%" fetch %GIT_REMOTE%
if errorlevel 1 (
  echo git fetch failed. Check your internet and repository access.
  pause
  exit /b 1
)

git -C "%ROOT_DIR%" pull %GIT_REMOTE% %GIT_BRANCH%
if errorlevel 1 (
  echo git pull failed. Check your internet and repository access.
  pause
  exit /b 1
)

echo.
echo Rebuilding and restarting IPCAS...
call "%ROOT_DIR%\customer\scripts\compose.bat" up -d --build --remove-orphans
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
echo IPCAS updated and running at %APP_URL%
echo.
pause
endlocal
