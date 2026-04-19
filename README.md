# Breadcrumbs

Breadcrumbs is a local workflow recorder that captures your app switches and in-app actions, filters out distractions using Claude AI, and generates a markdown summary + reusable automation skill from your session.

## What it does

1. **Records** — detects app switches instantly via Windows event hooks (no polling); captures DOM clicks from browsers, Electron apps, and Win32 apps
2. **Filters** — uses Claude to classify each action as on-path or drift based on your declared intent; drift screenshots are deleted
3. **Summarizes** — generates a markdown workflow summary of what you actually did
4. **Generates skills** — converts your filtered actions into an OpenClaw skill YAML for automation replay

## Capture Sources

| App Type | Examples | Method |
|----------|----------|--------|
| Browsers | Opera, Chrome, Edge | Browser extension (DOM selectors) |
| Electron apps | VS Code, Discord, Notion | Chrome DevTools Protocol |
| Win32 apps | Notepad, Word, Excel | Windows UI Automation |
| New Outlook | olk.exe | Electron (requires debug launch) |

## Project Structure

```
workflow-summarizer/
├── main.py               # Entry point, unified session orchestration
├── recorder.py           # Screenshot capture
├── blocker.py            # Blocklist checking (app + title patterns)
├── filter.py             # Claude API drift detection
├── summarizer.py         # Markdown workflow summary generation
├── skill_generator.py    # OpenClaw skill YAML generation
├── server.py             # Flask HTTP server for browser extension events
├── hooks.py              # Windows event hooks (instant app-switch detection)
├── electron_launcher.py  # Launch Electron apps with DevTools debug port
├── electron_capture.py   # Chrome DevTools Protocol DOM capture
├── uia_capture.py        # Windows UI Automation for Win32 apps
├── click_hook.py         # Global mouse hook + UIA element query
├── setup_electron.py     # Helper to launch Electron apps with debug ports
├── config.json           # API key, blocklists, settings (gitignored)
├── requirements.txt
└── extension/            # Browser extension (Chrome/Opera)
    ├── manifest.json
    ├── content.js
    └── background.js
```

## Setup

### 1. Install dependencies

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r workflow-summarizer\requirements.txt
```

### 2. Configure

Create `workflow-summarizer/config.json`:

```json
{
  "blocked_apps": ["1Password", "KeePass", "Bitwarden"],
  "blocked_title_patterns": ["bank", "chase", "paypal", "password", "sign in"],
  "anthropic_api_key": "sk-ant-...",
  "screenshot_dir": "output/screenshots",
  "capture_mode": "unified"
}
```

### 3. Install the browser extension

1. Open Opera → `opera://extensions` (or Chrome → `chrome://extensions`)
2. Enable **Developer mode**
3. Click **Load unpacked** → select the `workflow-summarizer/extension/` folder

### 4. Launch Electron apps with debug ports (optional)

To capture clicks inside VS Code, Discord, Notion:

```powershell
cd workflow-summarizer
& "..\venv\Scripts\python.exe" setup_electron.py
```

Select an app to relaunch it with the DevTools debug port enabled.

## Usage

**Terminal 1** — start the browser event server:
```powershell
& ".venv\Scripts\python.exe" workflow-summarizer\server.py
```

**Terminal 2** — start recording:
```powershell
cd workflow-summarizer
& "..\venv\Scripts\python.exe" main.py
```

Then:
1. Type your intent when prompted (e.g. `reply to email and update code`)
2. Work normally — switch apps, click around
3. Press **Ctrl+C** to stop recording

## Output

| File | Description |
|------|-------------|
| `output/raw.json` | All captured actions with DOM/UIA events |
| `output/filtered.json` | On-path actions only |
| `output/workflow.md` | Claude-generated markdown summary |
| `output/skills/<intent>.yaml` | OpenClaw automation skill |
| `output/screenshots/` | Screenshots for on-path actions only |

## Blocklist

Apps and window title patterns in `config.json` are always blocked — no screenshot, no API call:

```json
"blocked_apps": ["1Password", "KeePass", "Bitwarden"],
"blocked_title_patterns": ["bank", "chase", "paypal", "password", "sign in"]
```

## Requirements

- Windows 10/11
- Python 3.10+
- Opera or Chrome
- Anthropic API key
