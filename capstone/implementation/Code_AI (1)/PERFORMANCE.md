# Performance

Optimized for local Ollama on CPU/RAM-constrained systems.
- 2048 context
- short outputs
- 30m keep-alive
- no unnecessary LLM call in vulnerability scanner
- explanation uses 350-token response and one compact retry
- review/generation use compact prompts

Actual latency depends on local hardware and model.
