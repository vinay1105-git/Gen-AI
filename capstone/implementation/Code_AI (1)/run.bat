@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo Virtual environment not found. Run install.bat first.
  pause
  exit /b 1
)

where ollama >nul 2>&1 || (
  echo Ollama was not found on PATH. Install Ollama first.
  pause
  exit /b 1
)

set "OLLAMA_MODEL_FOUND="
for /f "skip=1 tokens=1" %%M in ('ollama list 2^>nul') do (
  if not defined OLLAMA_MODEL_FOUND set "OLLAMA_MODEL_FOUND=%%M"
)
if not defined OLLAMA_MODEL_FOUND (
  echo No Ollama models are installed. Install one once, for example: ollama pull llama3.2
  pause
  exit /b 1
)

rem Clean stale processes using this application's fixed ports.
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ports=8000,8501; foreach($port in $ports){$owners=(Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique); foreach($owner in $owners){if($owner -and $owner -ne $PID){Stop-Process -Id $owner -Force -ErrorAction SilentlyContinue}}}"

start "Code AI Backend" /b "%~dp0.venv\Scripts\python.exe" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000

set /a attempts=0
:wait_backend
set /a attempts+=1
powershell -NoProfile -Command "try { $r=Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/api/v1/health -TimeoutSec 2; if($r.StatusCode -eq 200){exit 0}else{exit 1} } catch { exit 1 }"
if not errorlevel 1 goto backend_ready
if %attempts% GEQ 30 (
  echo Backend did not become ready within 30 seconds.
  echo Check the backend process for an error.
  pause
  exit /b 1
)
timeout /t 1 /nobreak >nul
goto wait_backend

:backend_ready
echo Backend is ready at http://127.0.0.1:8000
start "Code AI Frontend" /b "%~dp0.venv\Scripts\python.exe" -m streamlit run frontend\app.py --server.headless true --server.port 8501
timeout /t 3 /nobreak >nul
start "" http://127.0.0.1:8501
endlocal
