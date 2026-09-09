import httpx
import re
from typing import List, Dict, Any, Optional
from app.core.config import settings

class OllamaClient:
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL.rstrip('/')
        self.model = settings.OLLAMA_MODEL
        self.embed_model = settings.OLLAMA_EMBED_MODEL
        self.timeout = max(35, settings.OLLAMA_TIMEOUT_SECONDS)

    def get_available_models(self) -> List[str]:
        try:
            with httpx.Client(timeout=3.0) as client:
                res = client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    models = res.json().get("models", [])
                    return [m.get("name", "") for m in models]
        except Exception:
            pass
        return []

    def get_active_model(self) -> str:
        """Return the best available model, preferring llama3.1:8b, then qwen3.5:9b, then configured."""
        full_names = self.get_available_models()
        if full_names:
            # Check for llama3.1 first
            for name in full_names:
                if "llama3.1" in name:
                    return name
            # Check for qwen3.5
            for name in full_names:
                if "qwen3.5" in name:
                    return name
            # Check for any chat model
            for name in full_names:
                if "embed" not in name:
                    return name
        return self.model

    def is_available(self) -> bool:
        try:
            with httpx.Client(timeout=2.0) as client:
                res = client.get(f"{self.base_url}/api/tags")
                return res.status_code == 200
        except Exception:
            return False

    def get_health(self) -> Dict[str, Any]:
        models = self.get_available_models()
        has_ollama = len(models) > 0
        active_llm = self.get_active_model() if has_ollama else "none"
        has_embed = any("embed" in m for m in models)
        return {
            "ollama_connected": has_ollama,
            "active_model": active_llm,
            "embedding_model": self.embed_model,
            "embedding_available": has_embed,
            "available_models": models
        }

    def generate(
        self, 
        prompt: str, 
        system: Optional[str] = None, 
        json_mode: bool = False, 
        model: Optional[str] = None,
        max_tokens: int = 750,
        temperature: float = 0.2
    ) -> Optional[str]:
        try:
            target_model = model or self.get_active_model()
            payload: Dict[str, Any] = {
                "model": target_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    "num_ctx": 4096
                }
            }
            if system:
                payload["system"] = system
            if json_mode:
                payload["format"] = "json"

            with httpx.Client(timeout=self.timeout) as client:
                res = client.post(f"{self.base_url}/api/generate", json=payload)
                if res.status_code == 200:
                    data = res.json()
                    resp = data.get("response", "")
                    # If response is empty but thinking has content
                    if not resp.strip() and data.get("thinking"):
                        resp = data.get("thinking", "")
                    # Strip any <think> tags
                    resp = re.sub(r'<think>.*?</think>', '', resp, flags=re.DOTALL).strip()
                    return resp if len(resp) > 3 else None
                return None
        except Exception as e:
            print(f"[OllamaClient] Generate error: {e}")
            return None

    def get_embedding(self, text: str) -> Optional[List[float]]:
        if not text or not text.strip():
            return None
        try:
            payload = {
                "model": self.embed_model,
                "prompt": text[:2000]
            }
            with httpx.Client(timeout=10.0) as client:
                res = client.post(f"{self.base_url}/api/embeddings", json=payload)
                if res.status_code == 200:
                    emb = res.json().get("embedding")
                    if emb and isinstance(emb, list) and len(emb) > 0:
                        return emb
                return None
        except Exception as e:
            print(f"[OllamaClient] Embedding error: {e}")
            return None

ollama_client = OllamaClient()
