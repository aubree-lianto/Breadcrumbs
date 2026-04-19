# Breadcrumbs

Breadcrumbs is a local workflow recorder that captures your app switches and browser clicks, filters out distractions using Claude AI, and generates a markdown summary + reusable automation skill from your session.

## What it does

1. **Records** — detects active window switches and captures screenshots; a browser extension captures DOM-level click events
2. **Filters** — uses Claude to classify each action as on-path or drift based on your declared intent
3. **Summarizes** — generates a markdown workflow summary of what you actually did
4. **Generates skills** — converts your filtered actions into an OpenClaw skill YAML for automation replay

## Project Structure

```
workflow-summarizer/
├── main.py              # Entry point, session orchestration
├── recorder.py          # Window detection, screenshot capture
├── blocker.py           # Blocklist checking (app + title patterns)
├── filter.py            # Claude API drift detection
├── summarizer.py        # Markdown workflow summary generation
├── skill_generator.py   # OpenClaw skill YAML generation
├── server.py            # Flask HTTP server for browser extension events
├── config.json          # API key, blocklists, settings (gitignored)
├── requirements.txt
└── extension/           # Browser extension (Chrome/Opera)
    ├── manifest.json
    ├── content.js
    └── background.js
```

## Setup

### 1. Install dependencies

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r workflow-summarizer/requirements.txt
```

### 2. Configure

Copy and edit `config.json`:

```json
{
  "blocked_apps": ["1Password", "KeePass", "Bitwarden"],
  "blocked_title_patterns": ["bank", "chase", "paypal", "password", "sign in"],
  "anthropic_api_key": "sk-ant-...",
  "screenshot_dir": "output/screenshots",
  "polling_interval_ms": 250
}
```

### 3. Install the browser extension

1. Open Opera → `opera://extensions` (or Chrome → `chrome://extensions`)
2. Enable **Developer mode**
3. Click **Load unpacked** → select the `workflow-summarizer/extension/` folder

## Usage

### Terminal 1 — start the browser event server

```bash
.venv\Scripts\python.exe workflow-summarizer\server.py
```

### Terminal 2 — start recording

```bash
cd workflow-summarizer
..\venv\Scripts\activate
python main.py
```

Then:
1. Type your intent when prompted (e.g. `create a github issue`)
2. Work normally — switch apps, click in the browser
3. Press **Ctrl+C** to stop recording

### Output

| File | Description |
|------|-------------|
| `output/raw.json` | All captured actions (minus hard-blocked apps) |
| `output/filtered.json` | On-path actions only |
| `output/workflow.md` | Claude-generated markdown summary |
| `output/skills/<intent>.yaml` | OpenClaw automation skill |
| `output/screenshots/` | Screenshots for on-path actions only |

## Blocklist

Apps and window title patterns in `config.json` are always blocked — no screenshot taken, no API call made:

```json
"blocked_apps": ["1Password", "KeePass", "Bitwarden"],
"blocked_title_patterns": ["bank", "chase", "paypal", "password", "sign in"]
```

## Requirements

- Windows 10/11
- Python 3.10+
- Opera or Chrome
- Anthropic API key
