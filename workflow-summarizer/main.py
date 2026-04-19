import json
import os
import sys
import time
import shutil
from datetime import datetime

# Ensure stdout handles arbitrary Unicode on Windows consoles
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf-16"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from anthropic import Anthropic

from recorder import get_active_window, capture_screenshot
from blocker import is_blocked
from filter import filter_session
from summarizer import generate_summary


def load_config(path: str) -> dict:
    with open(path) as f:
        config = json.load(f)
    if not config.get("anthropic_api_key"):
        config["anthropic_api_key"] = os.getenv("ANTHROPIC_API_KEY", "")
    return config


def save_json(data: list, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def save_markdown(text: str, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)


def record_session(intent: str, config: dict) -> list:
    actions = []
    last_hwnd = None

    print(f"Recording session. Intent: {intent}")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            window = get_active_window()

            if window["hwnd"] != last_hwnd:
                last_hwnd = window["hwnd"]

                if is_blocked(window["app"], window["title"], config):
                    print(f"[BLOCKED] {window['app']} - {window['title'][:50]}")
                    continue

                screenshot_path = capture_screenshot(config["screenshot_dir"])

                action = {
                    "timestamp": datetime.now().isoformat(),
                    "app": window["app"],
                    "title": window["title"],
                    "screenshot": screenshot_path,
                }
                actions.append(action)
                print(f"[CAPTURED] {window['app']} - {window['title'][:50]}")

            time.sleep(config["polling_interval_ms"] / 1000)

    except KeyboardInterrupt:
        print(f"\nSession ended. Captured {len(actions)} actions.")
        return actions


def main():
    config = load_config("config.json")

    if not config["anthropic_api_key"]:
        print("ERROR: No API key found. Set anthropic_api_key in config.json or ANTHROPIC_API_KEY env var.")
        return

    client = Anthropic(api_key=config["anthropic_api_key"])

    # Clean output dir at session start
    screenshot_dir = config["screenshot_dir"]
    if os.path.exists(screenshot_dir):
        shutil.rmtree(screenshot_dir)
    os.makedirs(screenshot_dir, exist_ok=True)

    intent = input("What are you working on? > ")

    # Record
    actions = record_session(intent, config)
    save_json(actions, "output/raw.json")

    # Filter
    filtered = filter_session(actions, intent, client)
    save_json(filtered, "output/filtered.json")

    # Summarize
    summary = generate_summary(filtered, intent, client)
    save_markdown(summary, "output/workflow.md")

    print(f"\nDone!")
    print(f"  Raw actions:  {len(actions)}")
    print(f"  Filtered:     {len(filtered)}")
    print(f"  Summary:      output/workflow.md")


if __name__ == "__main__":
    main()
