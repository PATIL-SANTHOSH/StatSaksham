import httpx
import re
from typing import List, Dict, Any, Optional
from app.core.config import settings

class OllamaClient:
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL.rstrip('/')
        self.model = settings.OLLAMA_MODEL
        self.embed_model = settings.OLLAMA_EMBED_MODEL
        self.timeout = settings.OLLAMA_TIMEOUT_SECONDS

    def get_active_model(self) -> str:
        """Return the best available model, preferring llama3.1:8b for direct, non-stalling chat."""
        try:
            with httpx.Client(timeout=1.5) as client:
                res = client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    models = res.json().get("models", [])
                    full_names = [m.get("name", "") for m in models]
                    # Check for llama3.1:8b first (fastest and clean chat)
                    for name in full_names:
                        if "llama3.1" in name:
                            return name
                    # Check for qwen3.5:9b
                    for name in full_names:
                        if "qwen3.5" in name:
                            return name
                    if full_names:
                        return full_names[0]
        except Exception:
            pass
        return self.model

    def is_available(self) -> bool:
        try:
            with httpx.Client(timeout=1.5) as client:
                res = client.get(f"{self.base_url}/api/tags")
                return res.status_code == 200
        except Exception:
            return False

    def generate(self, prompt: str, system: Optional[str] = None, json_mode: bool = False, model: Optional[str] = None) -> Optional[str]:
        try:
            target_model = model or self.get_active_model()
            payload: Dict[str, Any] = {
                "model": target_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 350,
                    "num_ctx": 2048
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
                    return resp if len(resp) > 5 else None
                return None
        except Exception as e:
            print(f"[OllamaClient] Generate error: {e}")
            return None

    def get_embedding(self, text: str) -> Optional[List[float]]:
        try:
            payload = {
                "model": self.embed_model,
                "prompt": text
            }
            with httpx.Client(timeout=6.0) as client:
                res = client.post(f"{self.base_url}/api/embeddings", json=payload)
                if res.status_code == 200:
                    return res.json().get("embedding")
                return None
        except Exception as e:
            print(f"[OllamaClient] Embedding error: {e}")
            return None

ollama_client = OllamaClient()
