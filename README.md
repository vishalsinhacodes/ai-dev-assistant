# AI Dev Assistant Agent

A production-grade agentic backend service built with FastAPI.

## What it does

Takes a developer question, autonomously decides which tools to call,
executes them in a ReAct loop, and returns a synthesised answer.

## Tools available

- `web_search` — DuckDuckGo search for current information
- `get_package_version` — PyPI API for exact package versions
- `read_file` — reads local files safely
- `run_python` — executes Python snippets in a sandboxed subprocess

## Tech stack

- FastAPI + Uvicorn
- OpenAI gpt-4.1-mini
- Manual JSON-based tool parsing (model-agnostic)
- Pydantic v2 for request/response validation

## Setup

```bash
pip install -r requirements.txt
# Add OPENAI_API_KEY to .env
uvicorn app.main:app --reload
```

## API

POST /agent/run
{"message": "What is the latest version of FastAPI?"}

## Project status

- [x] Milestone 1 — Tool use foundations
- [ ] Milestone 2 — ReAct loop
- [ ] Milestone 3 — Parallel tools + session memory
- [ ] Milestone 4 — SSE streaming
- [ ] Milestone 5 — MCP server
