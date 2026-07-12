@echo off
rem Run docker compose with customer stack files. Tries v2 plugin, then legacy docker-compose.
if not defined ROOT_DIR (
  set "ROOT_DIR=%~dp0..\.."
)
cd /d "%ROOT_DIR%"

if not defined COMPOSE_PROJECT_NAME (
  call "%ROOT_DIR%\customer\scripts\load-config.bat"
)

docker compose -f docker-compose.customer.yml %*
if not errorlevel 1 exit /b %ERRORLEVEL%

docker-compose -f docker-compose.customer.yml %*
exit /b %ERRORLEVEL%
