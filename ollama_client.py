"""Minimal Ollama HTTP client — stdlib only (urllib).

One 8B model in RAM at a time: every call sends keep_alive=0m so Ollama
unloads the model as soon as the call ends, freeing RAM for the next
specialist. num_ctx 8192 keeps the KV cache small on 16 GB RAM.
"""
import json
import urllib.error
import urllib.request


class OllamaError(Exception):
    """Ollama is unreachable, or answered something unexpected."""


class OllamaClient:
    def __init__(self, base_url, num_ctx=8192, timeout=600):
        self.base_url = base_url.rstrip("/")
        self.num_ctx = num_ctx
        self.timeout = timeout

    def chat(self, model, messages, temperature=0.2):
        """One /api/chat call (stream off). Returns the reply text."""
        body = json.dumps({
            "model": model,
            "messages": messages,
            "stream": False,
            "keep_alive": "0m",
            "options": {"num_ctx": self.num_ctx, "temperature": temperature},
        }).encode("utf-8")
        req = urllib.request.Request(
            self.base_url + "/api/chat", data=body,
            headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read())
        except urllib.error.URLError as e:
            raise OllamaError(f"Could not reach Ollama at {self.base_url}: {e}")
        try:
            return data["message"]["content"]
        except (KeyError, TypeError):
            raise OllamaError(f"Unexpected reply from Ollama for model {model}.")

    def tags(self):
        """Names of the models Ollama has pulled. Raises OllamaError if down."""
        try:
            with urllib.request.urlopen(self.base_url + "/api/tags", timeout=10) as resp:
                data = json.loads(resp.read())
        except urllib.error.URLError as e:
            raise OllamaError(f"Could not reach Ollama at {self.base_url}: {e}")
        return [m["name"] for m in data.get("models", [])]

    def version(self):
        """Ollama server version, or '?' when the endpoint is missing."""
        try:
            with urllib.request.urlopen(self.base_url + "/api/version", timeout=10) as resp:
                return json.loads(resp.read()).get("version", "?")
        except Exception:
            return "?"
