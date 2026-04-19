import json
import os
import sys
import shutil

import requests as http_requests

# Ensure stdout handles arbitrary Unicode on Windows consoles
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf-16"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from anthropic import Anthropic

from recorder import capture_screenshot
from blocker import is_blocked
from filter import filter_session
from summarizer import generate_summary
from skill_generator import generate_skill, save_skill
from hooks import start_event_hook, get_next_event, clear_events


def load_config(path: str) -> dict:
    with open(path) as f:
        config = json.load(f)
    if not config.get("anthropic_api_key"):
        config["anthropic_api_key"] = os.getenv("ANTHROPIC_API_KEY", "")
    return config


def save_json(data: list, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def save_markdown(text: str, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def get_browser_events() -> list:
    try:
        events = http_requests.get('http://127.0.0.1:8000/events', timeout=1).json()
        http_requests.delete('http://127.0.0.1:8000/events', timeout=1)
        return events
    except Exception:
        return []


def record_session(intent: str, config: dict) -> list:
    actions = []

    print(f"Recording session. Intent: {intent}")
    print("Press Ctrl+C to stop.")
    print("[MODE] Event-driven (no polling)")
    print("Make sure browser extension is installed and server.py is running.\n")

    # Clear stale events
    clear_events()
    try:
        http_requests.delete('http://127.0.0.1:8000/events', timeout=1)
    except Exception:
        print("[WARN] Browser event server not running — browser events won't be captured")

    start_event_hook()

    try:
        while True:
            event = get_next_event(timeout=1.0)

            if event is None:
                continue

            if is_blocked(event["app"], event["title"], config):
                print(f"[BLOCKED] {event['app']} - {event['title'][:50]}")
                continue

            screenshot_path = capture_screenshot(config["screenshot_dir"])
            browser_events = get_browser_events()

            action = {
                "type": "app_switch",
                "timestamp": event["timestamp"],
                "app": event["app"],
                "title": event["title"],
                "exe_path": event.get("exe_path"),
                "pid": event.get("pid"),
                "screenshot": screenshot_path,
                "browser_events": browser_events,
            }
            actions.append(action)
            print(f"[CAPTURED] {event['app']} - {event['title'][:40]} ({len(browser_events)} browser events)")

    except KeyboardInterrupt:
        final_events = get_browser_events()
        if final_events and actions:
            actions[-1]["browser_events"].extend(final_events)

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
    print("\n[RECORDING]")
    actions = record_session(intent, config)
    save_json(actions, "output/raw.json")

    # Filter
    print("\n[FILTERING]")
    filtered = filter_session(actions, intent, client)
    save_json(filtered, "output/filtered.json")

    # Summarize
    print("\n[SUMMARIZING]")
    summary = generate_summary(filtered, intent, client)
    save_markdown(summary, "output/workflow.md")

    # Generate skill
    print("\n[GENERATING SKILL]")
    skill_yaml = generate_skill(filtered, intent, client)
    skill_path = save_skill(skill_yaml, intent, "output/skills")

    print(f"\nDone!")
    print(f"  Raw actions:  {len(actions)}")
    print(f"  Filtered:     {len(filtered)}")
    print(f"  Summary:      output/workflow.md")
    print(f"  Skill:        {skill_path}")


if __name__ == "__main__":
    main()
