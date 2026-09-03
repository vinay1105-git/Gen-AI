@echo off
setlocal
cd /d "%~dp0"
where python >nul 2>&1 || (echo Python was not found on PATH.& pause & exit /b 1)
if not exist ".venv\Scripts\python.exe" python -m venv .venv
call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt || (echo Dependency installation failed.& pause & exit /b 1)
python -m pip show email-validator >nul 2>&1 || (echo email-validator is missing.& pause & exit /b 1)
python -m compileall backend frontend >nul || (echo Python compilation failed.& pause & exit /b 1)
echo.
echo Installation completed successfully.
echo Ollama model expected: llama3.2:latest
echo Run run.bat to start backend and frontend.
endlocal
