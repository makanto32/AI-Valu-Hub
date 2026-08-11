@echo off
setlocal
set "ROOT=%~dp0"
set "PORT=%~1"
if "%PORT%"=="" set "PORT=8080"
set "PYTHON_EXE=%ROOT%.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" set "PYTHON_EXE=python"
start "HTML Preview" cmd /k "cd /d "%ROOT%" && "%PYTHON_EXE%" -m http.server %PORT%"
ping -n 3 127.0.0.1 >nul
start "" http://127.0.0.1:%PORT%/index.html
echo.
echo Vista previa lista en http://127.0.0.1:%PORT%/index.html
echo.
endlocal
