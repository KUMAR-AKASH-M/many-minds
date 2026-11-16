@echo off
REM Pull the three v1 models for many-minds (~12 GB total, one-time download).
ollama pull qwen3:8b
ollama pull qwen2.5-coder:7b
ollama pull qwen3:4b
ollama list
