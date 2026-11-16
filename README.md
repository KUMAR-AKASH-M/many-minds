# many-minds

An offline agent CLI: several small specialist models working together, so
you get better answers than any one small model alone — instead of needing
one big model. Runs on your own machine, no cloud, no account, no cost
after the one-time model downloads.

## The idea

One model at a time, each doing what it is best at:

| Role | Model | Size | Job |
|---|---|---|---|
| Planner | `qwen3:8b` | ~5 GB | Breaks a task into steps, answers chat |
| Coder | `qwen2.5-coder:7b` | ~4.7 GB | Writes the code |
| Reviewer | `qwen3:4b` | ~2.5 GB | Checks the code, lists real fixes |

Only one 8B model sits in RAM at a time (`keep_alive=0m`), so it fits a
16 GB laptop. Add more models or roles any time: pull the model with
Ollama, add one entry to `roles.json` — no code changes.

## Setup (Windows, one time)

1. Install [Ollama](https://ollama.com/download) and start it.
2. Pull the three v1 models (~12 GB total, one-time download):
   run `pull-models.bat`, or:
   ```
   ollama pull qwen3:8b
   ollama pull qwen2.5-coder:7b
   ollama pull qwen3:4b
   ```
3. Check everything is ready:
   ```
   python agent.py --check
   ```

## Use (M1)

```
python agent.py chat      # interactive REPL with the planner
python agent.py --check   # Ollama up? which models are pulled?
python agent.py --version
```

In the REPL: type a question, get an answer. `/reset` starts fresh,
`/exit` quits. Each session is saved to
`%USERPROFILE%\.many-minds\sessions\` as one `.jsonl` file.

## Speed to expect

5–15 tokens/sec for the 8B model on a laptop CPU (12th-gen i5). A short
answer takes seconds; a code task takes a couple of minutes. This is a
small-models agent, not a frontier model — it is good at small, concrete
jobs, not at big complex projects in one go.

## Config-first: add your own models and roles

`roles.json` is the whole roster. Each role is a name, a model, a system
prompt, a temperature and the tools it may use. To add a model:

1. `ollama pull <model>`
2. Add one entry under `"roles"` in `roles.json`.

No code changes, no rebuild. The same file can point a role at a
different model later (e.g. a 14B planner, if your RAM allows it).

Memory lives in one global folder (`%USERPROFILE%\.many-minds\`) so facts
follow you across projects. Point it elsewhere with the
`MANY_MINDS_MEMORY_DIR` env var or a `"memory_dir"` key in a `config.json`
next to `agent.py`.

## What's next

- **M2** — memory: `remember` / `recall` across restarts (plain files).
- **M3** — files + shell tools, gated: every shell command needs your
  `y` first; destructive commands stay blocked.
- **M4** — code loop wired in: planner → coder → reviewer → one fix pass.
- **M5** — first real task, end to end. Only then talk about a VPS.

## VPS later

Same Ollama + same CLI, pointed at the server. Only Oracle Cloud's
always-free Ampere VM (up to 24 GB RAM) fits the 8B models; it needs a
card on file even for the free tier. Fly.io / Render free tiers (512 MB–
1 GB) are too small. Never expose Ollama's port publicly — SSH tunnel.
