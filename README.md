# Computer-Use Agent Scaffold

This repository provides a minimal, production-minded scaffold for "computer-use" agents across web and non-web (desktop and mobile) environments.

- Planner: simple rule-based planner (default) with an optional OpenAI tool-calling planner
- Schema: strict JSON Action schema (click/type/scroll/wait_for, plus non-web extensions)
- Executors: web executor using Playwright (runnable on Linux), stubs/hooks for desktop and mobile
- Runner: CLI to run tasks
- Tracing: per-step logs and screenshots

## Why this scaffold
- Start fast with web automation that is robust (DOM-first, bbox fallback)
- Keep non-web in mind with action schema and planner abstractions you can extend
- Lazy imports so `--help` works without installing heavy deps

## Requirements
- Python 3.10+
- Linux/macOS/Windows (web path tested on Linux)

Optional:
- OpenAI API key for the OpenAI planner: set `OPENAI_API_KEY`

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Install browsers for Playwright (once):
python -m playwright install --with-deps
```

## Quickstart (Web)

Run a simple task that clicks an element by CSS selector.

```bash
python -m agent.runner \
  --platform web \
  --url https://example.org \
  --goal "click selector=a"
```

- The rule-based planner recognizes goals like `click selector=...`, `type selector=... text=...`, `wait_for selector=...`.
- Traces are written to `./traces/<timestamp>/`.

Use the OpenAI planner (optional):

```bash
export OPENAI_API_KEY=sk-...  # or set via your secret manager
python -m agent.runner \
  --platform web \
  --planner openai \
  --url https://example.org \
  --goal "Open the first link on the page and wait for navigation"
```

## Desktop and Mobile (non-web)
This scaffold includes the action schema and planner hooks for desktop/mobile, but the executors are placeholders. Implementations vary by OS:

- Desktop (Linux/Windows/macOS): prefer Accessibility APIs (AT-SPI/UIA/AX) and fall back to pixel actions
- Mobile (Android/iOS): prefer UI hierarchy (uiautomator2/WDA) via Appium; fall back to image crops when needed

You can add your own executors under `agent/executors/desktop_executor.py` and `agent/executors/mobile_executor.py`.

## Project layout

- `agent/planner/schema.py` — strict JSON action schema
- `agent/planner/simple_planner.py` — rule-based planner for demo goals
- `agent/planner/openai_planner.py` — optional OpenAI planner with tool-calling
- `agent/executors/web_executor.py` — Playwright-based web executor
- `agent/runner.py` — CLI entrypoint
- `agent/tracing.py` — lightweight tracing utilities

## Notes
- Keep planner messages small by sending DOM and cropped screenshots; prefer DOM selectors when available.
- For desktop/mobile, add assertions based on accessibility trees to increase reliability.

## License
MIT 