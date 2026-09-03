@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Virtual environment not found. Run install.bat first.
  exit /b 1
)
".venv\Scripts\python.exe" -m compileall -q backend frontend || (
  echo Python compilation check FAILED.
  exit /b 1
)
".venv\Scripts\python.exe" -c "import email_validator, fastapi, sqlalchemy, requests; print('Core dependency check: OK')" || (
  echo Core dependency check FAILED.
  exit /b 1
)
where ollama >nul 2>&1 || (
  echo Ollama is not on PATH.
  exit /b 1
)
ollama list
if errorlevel 1 (
  echo Ollama check FAILED.
  exit /b 1
)
echo.
echo CODE AI verification completed: syntax and core dependencies OK.
echo If the application is running, open http://127.0.0.1:8501
endlocal
