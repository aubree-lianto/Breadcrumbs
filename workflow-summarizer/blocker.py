def is_blocked(app: str, title: str, config: dict) -> bool:
    app_lower = app.lower()
    title_lower = title.lower()

    for blocked_app in config["blocked_apps"]:
        if blocked_app.lower() in app_lower:
            return True

    for pattern in config["blocked_title_patterns"]:
        if pattern.lower() in title_lower:
            return True

    return False
