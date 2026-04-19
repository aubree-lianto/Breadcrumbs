import os
from anthropic import Anthropic


def check_drift(action: dict, intent: str, recent_actions: list, client: Anthropic) -> bool:
    """Returns True if action is on-path, False if drift."""
    context = "\n".join([f"- {a['app']}: {a['title']}" for a in recent_actions[-5:]])

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=50,
        messages=[{
            "role": "user",
            "content": f"""User's declared intent: "{intent}"

Recent actions:
{context}

Current action:
- App: {action['app']}
- Window: {action['title']}

Is this action on-path (directly supporting the intent) or drift (distraction/unrelated)?

Respond with exactly one word: ON-PATH or DRIFT"""
        }]
    )

    result = response.content[0].text.strip().upper()
    return "ON-PATH" in result


def filter_session(actions: list, intent: str, client: Anthropic) -> list:
    filtered = []

    for i, action in enumerate(actions):
        is_on_path = check_drift(action, intent, actions[:i], client)

        if is_on_path:
            action["status"] = "on-path"
            filtered.append(action)
        else:
            action["status"] = "drift"
            if os.path.exists(action["screenshot"]):
                os.remove(action["screenshot"])
                print(f"[DELETED] {action['screenshot']}")

    return filtered
