"""Config-first setup for many-minds: roles live in roles.json, not in code.

Adding a model = `ollama pull <model>` + one entry in roles.json.
Adding a role = one entry in roles.json. No code changes.

Memory lives in one global folder under the user profile by default
(%USERPROFILE%\\.many-minds\\ on Windows, ~/.many-minds/ elsewhere).
Override it with the MANY_MINDS_MEMORY_DIR env var, or a "memory_dir"
key in a config.json next to agent.py.
"""
import json
import os
from pathlib import Path

APP_NAME = "many-minds"
DEFAULT_MEMORY_DIR = Path.home() / f".{APP_NAME}"
ENV_MEMORY_DIR = "MANY_MINDS_MEMORY_DIR"
ENV_OLLAMA_URL = "MANY_MINDS_OLLAMA_URL"


def project_dir():
    return Path(__file__).resolve().parent


def roles_path():
    return project_dir() / "roles.json"


def load_roles():
    """Parsed roles.json: ollama_url, num_ctx, roles{ name: model/system/... }."""
    with open(roles_path(), encoding="utf-8") as f:
        return json.load(f)


def memory_dir():
    env = os.environ.get(ENV_MEMORY_DIR)
    if env:
        return Path(env).expanduser()
    cfg = project_dir() / "config.json"
    if cfg.exists():
        try:
            with open(cfg, encoding="utf-8") as f:
                override = json.load(f).get("memory_dir")
            if override:
                return Path(override).expanduser()
        except (json.JSONDecodeError, OSError):
            pass
    return DEFAULT_MEMORY_DIR


def ollama_url(cfg):
    return os.environ.get(ENV_OLLAMA_URL) or cfg.get(
        "ollama_url", "http://localhost:11434")
