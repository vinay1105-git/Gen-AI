import logging
import threading
import time
from typing import Optional
import requests

logger = logging.getLogger(__name__)

class OllamaAdapter:
    """Fast local Ollama adapter with model-list caching and optimized defaults."""
    def __init__(self, host: str = "http://127.0.0.1:11434"):
        self.host = host.rstrip("/")
        self.session = requests.Session()
        self._models = []
        self._models_at = 0.0
        self._lock = threading.Lock()

    def health(self, timeout: float = 1.5) -> bool:
        try:
            return self.session.get(f"{self.host}/api/tags", timeout=timeout).ok
        except requests.RequestException:
            return False

    def list_models(self, timeout: float = 2.0, force: bool = False) -> list[str]:
        with self._lock:
            if not force and self._models and time.monotonic() - self._models_at < 30:
                return list(self._models)
        try:
            r = self.session.get(f"{self.host}/api/tags", timeout=timeout)
            r.raise_for_status()
            models = [m.get("name") for m in r.json().get("models", []) if m.get("name")]
            with self._lock:
                self._models, self._models_at = models, time.monotonic()
            return models
        except (requests.RequestException, ValueError) as exc:
            logger.warning("Unable to list Ollama models: %s", exc)
            return list(self._models)

    def detect(self) -> bool:
        return self.health()

    def generate(self, model: str, prompt: str, temperature: float = 0.1, max_tokens: int = 400, timeout: int = 90) -> Optional[str]:
        models = self.list_models()
        if not models:
            raise RuntimeError(f"Ollama is not reachable at {self.host} or no local models are installed.")
        if model not in models:
            if f"{model}:latest" in models:
                model = f"{model}:latest"
            else:
                raise RuntimeError(f"Model '{model}' is not installed. Available: {', '.join(models)}")
        payload = {
            "model": model, "prompt": prompt, "stream": False, "keep_alive": "30m",
            "options": {
                "temperature": float(temperature), "num_predict": int(max_tokens),
                "num_ctx": 2048, "top_p": 0.9, "repeat_penalty": 1.05,
            },
        }
        try:
            r = self.session.post(f"{self.host}/api/generate", json=payload, timeout=timeout)
            r.raise_for_status()
            text = r.json().get("response", "")
            return text.strip() or None
        except requests.Timeout as exc:
            raise TimeoutError("Model generation timed out. Falling back to local deterministic generation.") from exc
        except requests.RequestException as exc:
            detail = r.text[:500] if 'r' in locals() else ''
            raise RuntimeError(f"Ollama request failed: {exc}. {detail}") from exc

