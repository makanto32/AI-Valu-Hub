@echo off
setlocal

REM Usage:
REM   start-local-session.bat [API_HOST] [API_PORT] [FRONTEND_HOST] [FRONTEND_PORT]

set "ROOT=%~dp0"
set "API_HOST=%~1"
set "API_PORT=%~2"
set "FRONTEND_HOST=%~3"
set "FRONTEND_PORT=%~4"

if "%API_HOST%"=="" set "API_HOST=127.0.0.1"
if "%API_PORT%"=="" set "API_PORT=8000"
if "%FRONTEND_HOST%"=="" set "FRONTEND_HOST=127.0.0.1"
if "%FRONTEND_PORT%"=="" set "FRONTEND_PORT=5174"

set "API_BASE=http://%API_HOST%:%API_PORT%"
set "FRONT_URL=http://%FRONTEND_HOST%:%FRONTEND_PORT%"
set "PYTHON_EXE=%ROOT%.venv\Scripts\python.exe"
set "ENV_LOCAL=%ROOT%frontend\.env.local"

if not exist "%PYTHON_EXE%" (
  echo [ERROR] No se encontro Python virtualenv en: %PYTHON_EXE%
  echo Crea el entorno .venv antes de ejecutar este script.
  exit /b 1
)

echo VITE_API_URL=%API_BASE%> "%ENV_LOCAL%"

start "API Local" cmd /k "cd /d "%ROOT%" && "%PYTHON_EXE%" -m uvicorn api.app.main:app --host %API_HOST% --port %API_PORT% --reload"
start "Frontend Local" cmd /k "cd /d "%ROOT%frontend" && npm run dev -- --host %FRONTEND_HOST% --port %FRONTEND_PORT%"

echo.
echo ==========================================
echo   Sesion local iniciada
echo   API:      %API_BASE%/health
echo   Frontend: %FRONT_URL%
echo ==========================================
echo.
echo Usuario demo: analista.finanzas / demo123
echo.

start "" "%FRONT_URL%"

endlocal
