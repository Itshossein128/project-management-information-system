@echo off
setlocal EnableExtensions
cd /d "%~dp0\.."
set "ROOT_DIR=%CD%"

call "%ROOT_DIR%\customer\scripts\load-config.bat"

docker info >nul 2>&1
if errorlevel 1 (
  echo Docker is not running.
  pause
  exit /b 1
)

echo.
echo Stopping IPCAS...
call "%ROOT_DIR%\customer\scripts\compose.bat" down

echo.
echo IPCAS stopped. Your data is kept in Docker volumes.
echo Run start.bat to start again.
echo.
pause
endlocal
