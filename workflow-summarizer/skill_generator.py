import json
import os
import re

from anthropic import Anthropic


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s]+', '-', text)
    return text[:50]


def generate_skill(filtered_actions: list, intent: str, client: Anthropic) -> str:
    flat_actions = []
    for action in filtered_actions:
        flat_actions.append({
            "type": action.get("type"),
            "timestamp": action.get("timestamp"),
            "app": action.get("app"),
            "title": action.get("title"),
            "app_type": action.get("app_type", "unknown"),
            "event_source": action.get("event_source", "unknown"),
        })
        for event in action.get("dom_events", action.get("browser_events", [])):
            flat_actions.append({
                "type": event.get("type"),
                "timestamp": event.get("timestamp"),
                "url": event.get("url"),
                "element": event.get("element"),
                "key": event.get("key")
            })

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[{
            "role": "user",
            "content": f"""Convert these recorded user actions into an OpenClaw skill.

## User's Intent
"{intent}"

## Recorded Actions
```json
{json.dumps(flat_actions, indent=2)}
```

## Output Format
Generate a valid OpenClaw skill YAML. Follow this structure:

```yaml
name: {slugify(intent)}
description: "{intent}"
variables:
  - name: variable_name
    description: "What this variable is for"
    default: "optional default"
steps:
  - action: navigate
    url: "https://..."
  - action: click
    selector: "css selector here"
    description: "What this click does"
  - action: type
    selector: "css selector for input"
    value: "{{{{variable_name}}}}"
  - action: click
    selector: "submit button selector"
  - action: wait
    seconds: 1
```

## Locator Types
Actions may come from different sources — use the right action type:

1. Browser/Electron (DOM selectors):
   - action: click, selector: "#id" or "[aria-label='...']"

2. Win32 UIA locators:
   - action: uia_click, locator: "AutomationId:btnReply" or "Button:Name=Delete"
   - app: "OUTLOOK.EXE"

## Rules
1. Use the most specific selector available (prefer #id, [data-testid], [aria-label] over tag.class paths)
2. For UIA events use the locator field, not selector
3. Identify values that should be variables (things the user typed, selected, etc.)
4. Add wait steps after navigation or form submission
5. Add a description to each click explaining its purpose
6. Skip redundant clicks (multiple clicks on same element)
7. Output ONLY the YAML, no explanation or markdown fences
"""
        }]
    )

    return response.content[0].text


def save_skill(yaml_content: str, intent: str, output_dir: str) -> str:
    os.makedirs(output_dir, exist_ok=True)

    filename = f"{slugify(intent)}.yaml"
    filepath = os.path.join(output_dir, filename)

    yaml_content = yaml_content.strip()
    if yaml_content.startswith('```'):
        yaml_content = '\n'.join(yaml_content.split('\n')[1:])
    if yaml_content.endswith('```'):
        yaml_content = '\n'.join(yaml_content.split('\n')[:-1])

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(yaml_content)

    return filepath
