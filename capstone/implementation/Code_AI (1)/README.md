# Code AI

LLM-Based Multi-Agent Code Generation, Review, and Vulnerability Explanation System with Local LLM Deployment.

## Features
- Local Ollama LLM deployment
- Automatic code generation
- AI code review
- Static vulnerability scanning with CWE/severity/risk
- Code explanation with fast AI response and deterministic fallback
- Two-model comparison with parallel execution, timing and ranking
- History and system diagnostics
- SQLite persistence
- No cloud API key required
- No token or temperature controls exposed in the UI

## First run (Windows)
1. Make sure Ollama is installed and at least one model is installed, for example `ollama pull llama3.2`.
2. Run `install.bat` once in this folder.
3. Run `run.bat` for every normal launch.

## Normal run
```cmd
cd /d "C:\Users\gurka\Downloads\Code AI" && run.bat
```

The browser opens at `http://127.0.0.1:8501`. Backend docs are at `http://127.0.0.1:8000/docs`.

## Verification
After installation, run `verify.bat`. It checks Python compilation, core dependencies including `email-validator`, and Ollama availability.

## Model comparison
Install two Ollama models once. Example:
```cmd
ollama pull llama3.2
ollama pull qwen2.5-coder:1.5b
```
The application never downloads models automatically.

## Performance
The app uses short prompts, 2048 context, warm Ollama sessions and offloaded backend inference. Code explanation attempts AI for up to 5 seconds and then returns a local explanation, so the explanation page does not remain stuck if the local model is slow.
