@echo off
rem Load customer/ipcas.config into environment variables.
rem Caller must set ROOT_DIR before calling this script.

if not defined ROOT_DIR (
  echo ROOT_DIR is not set
  exit /b 1
)

set "GIT_REMOTE=origin"
set "GIT_BRANCH=main"
set "APP_URL=http://localhost:8080"
set "HEALTH_URL=http://localhost:8080/api/schema/"
set "WAIT_MAX_ATTEMPTS=90"
set "WAIT_INTERVAL_SEC=2"
set "COMPOSE_PROJECT_NAME=ipcas"

if exist "%ROOT_DIR%\customer\ipcas.config" (
  for /f "usebackq eol=# tokens=1,* delims==" %%A in ("%ROOT_DIR%\customer\ipcas.config") do (
    if not "%%~A"=="" set "%%~A=%%~B"
  )
)
