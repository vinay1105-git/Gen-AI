import logging
import shutil
import platform
import psutil
from typing import List

logger = logging.getLogger(__name__)


def detect_ollama() -> bool:
    """Return True if `ollama` is on PATH."""
    return shutil.which("ollama") is not None


def recommend_install_command_windows() -> str:
    return (
        "choco install ollama -y  # Or follow instructions at https://ollama.com/docs/installation"
    )


def detect_ram_gb() -> float:
    try:
        return round(psutil.virtual_memory().total / (1024 ** 3), 2)
    except Exception:
        return 0.0


def choose_model(available_models: List[str]) -> str:
    """Pick the largest compatible model based on available RAM.

    Preference order is external; caller should pass candidate model names.
    This function simply picks the first model that seems compatible with RAM.
    """
    ram = detect_ram_gb()
    logger.info("Detected RAM: %s GB", ram)

    # Heuristic sizes (GB) for common models
    model_requirements = {
        "Qwen2.5-Coder:7B": 10,
        "DeepSeek-Coder": 8,
        "code-llama": 12,
        "llama-3-2": 16,
    }

    for m in available_models:
        req = model_requirements.get(m, 6)
        if ram >= req:
            logger.info("Selected model %s (requires %s GB)", m, req)
            return m

    # fallback to first
    return available_models[0] if available_models else ""
