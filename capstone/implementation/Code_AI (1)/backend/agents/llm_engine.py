import logging
import re
from typing import Optional
from backend.config import settings, BASE_DIR
from backend.agents.ollama_adapter import OllamaAdapter
logger=logging.getLogger(__name__)

class LocalLLMEngine:
    def __init__(self, model_name: Optional[str]=None):
        self.ollama=OllamaAdapter(settings.OLLAMA_HOST)
        configured = model_name or settings.LOCAL_LLM_MODEL or settings.OLLAMA_MODEL
        # Reuse the last selected local model when it is still installed.
        try:
            selected = (BASE_DIR / ".selected_model").read_text(encoding="utf-8").strip()
            if selected:
                configured = selected
        except OSError:
            pass
        self.model_name=configured
    def generate_text(self,prompt:str,temperature:float=0.1,max_tokens:int=450,timeout:int=45)->str:
        if not prompt.strip(): raise ValueError("Prompt cannot be empty")
        if len(prompt)>9000: prompt=prompt[:6500]+"\n[context shortened]\n"+prompt[-1800:]
        out=self.ollama.generate(self.model_name,prompt,temperature=temperature,max_tokens=max_tokens,timeout=timeout)
        if not out: raise RuntimeError("Ollama returned an empty response")
        return self._clean_response(out)
    def available_models(self)->list[str]: return self.ollama.list_models() or [self.model_name]
    def current_model(self)->str: return self.model_name
    def status(self)->dict:
        models=self.ollama.list_models()
        return {"provider":"ollama","host":settings.OLLAMA_HOST,"reachable":bool(models) or self.ollama.health(),"model":self.model_name,"installed_models":models}
    @staticmethod
    def _clean_response(text:str)->str:
        text=re.sub(r"^```[a-zA-Z0-9_+.-]*\s*","",text.strip()); text=re.sub(r"\s*```$","",text); return text.strip()
