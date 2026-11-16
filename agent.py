#!/usr/bin/env python3
"""many-minds — an offline agent CLI: small specialist models working together.

M1: chat REPL (planner model) + --check (Ollama up? which models pulled?).
Stdlib only. One 8B model in RAM at a time (keep_alive=0m, num_ctx=8192).

Usage (Windows, in a terminal in this folder):
  python agent.py chat      # interactive REPL with the planner (qwen3:8b)
  python agent.py --check   # check Ollama + pulled models, then exit
  python agent.py --version

Requires Ollama running locally. First run once:
  ollama pull qwen3:8b
  ollama pull qwen2.5-coder:7b
  ollama pull qwen3:4b
(or run pull-models.bat)
"""
import argparse
import json
import sys
import time

from config import load_roles, memory_dir, ollama_url
from memory import save_session
from ollama_client import OllamaClient, OllamaError

VERSION = "0.1.0-m1"


def cmd_check(client, cfg):
    """Ollama up? Which of the three role models are pulled?"""
    try:
        models = client.tags()
    except OllamaError as e:
        print(f"Ollama is not reachable: {e}")
        print("Start the Ollama app, or run: ollama serve")
        return 1
    print(f"Ollama is up (version {client.version()}). Models pulled:")
    for m in models or ["(none yet — run pull-models.bat)"]:
        print(f"  - {m}")
    missing = [r["model"] for r in cfg["roles"].values() if r["model"] not in models]
    for m in missing:
        print(f"  ! missing: {m}  ->  ollama pull {m}")
    if missing:
        print("Run pull-models.bat, then check again.")
        return 1
    print("All three role models are ready.")
    return 0


def cmd_chat(client, cfg):
    """Interactive REPL with the planner model; multi-turn, history in session."""
    planner = cfg["roles"]["planner"]
    model = planner["model"]
    system = planner.get("system", "")
    temperature = planner.get("temperature", 0.3)
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    print(f"many-minds {VERSION} — chatting with {model} (planner).")
    print("Type /help for commands, /exit to quit. History stays in this session.")
    try:
        while True:
            try:
                text = input("you> ").strip()
            except EOFError:
                print()
                break
            if not text:
                continue
            if text in ("/exit", "/quit"):
                break
            if text == "/help":
                print("  /reset  start a fresh conversation")
                print("  /exit   quit (the session is saved)")
                continue
            if text == "/reset":
                messages = messages[:1] if system else []
                print("(fresh conversation)")
                continue
            messages.append({"role": "user", "content": text})
            t0 = time.time()
            try:
                reply = client.chat(model, messages, temperature=temperature)
            except OllamaError as e:
                messages.pop()
                print(f"\n[error] {e}", file=sys.stderr)
                print("Is Ollama running? Start the Ollama app, or run: ollama serve",
                      file=sys.stderr)
                continue
            messages.append({"role": "assistant", "content": reply})
            print(f"\n{reply}\n[{int(time.time() - t0)}s]")
    except KeyboardInterrupt:
        print("\n(interrupted)")
    path = save_session(memory_dir(), model, messages)
    print(f"Session saved to {path}")
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="agent",
        description="many-minds — offline agent CLI (M1: chat + check).")
    p.add_argument("command", nargs="?", choices=["chat"],
                   help="start the chat REPL")
    p.add_argument("--check", action="store_true",
                   help="Check Ollama and pulled models, then exit")
    p.add_argument("--version", action="store_true",
                   help="Print version and exit")
    args = p.parse_args(argv)
    if args.version:
        print(f"many-minds {VERSION}")
        return 0
    try:
        cfg = load_roles()
    except FileNotFoundError:
        print("[error] roles.json not found next to agent.py", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"[error] roles.json is not valid JSON: {e}", file=sys.stderr)
        return 1
    client = OllamaClient(ollama_url(cfg), num_ctx=cfg.get("num_ctx", 8192))
    if args.check:
        return cmd_check(client, cfg)
    if args.command == "chat":
        return cmd_chat(client, cfg)
    p.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
