from anthropic import Anthropic


def generate_summary(filtered_actions: list, intent: str, client: Anthropic) -> str:
    action_list = "\n".join([
        f"- [{a['timestamp']}] {a['app']}: {a['title']}"
        for a in filtered_actions
    ])

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": f"""The user declared this intent: "{intent}"

Here are the actions they took (filtered to only relevant actions):

{action_list}

Write a concise markdown workflow summary:
1. What they accomplished
2. The sequence of steps (numbered)
3. Key apps/tools used
4. Any patterns worth noting

Keep it under 300 words. Use markdown formatting."""
        }]
    )

    return response.content[0].text
