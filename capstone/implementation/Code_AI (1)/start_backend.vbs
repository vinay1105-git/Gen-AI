Set shell = CreateObject("WScript.Shell")
project = shell.CurrentDirectory
python = project & "\\.venv\\Scripts\\python.exe"
cmd = """" & python & """ -m uvicorn backend.main:app --host 127.0.0.1 --port 8000"
shell.Run cmd, 0, False
