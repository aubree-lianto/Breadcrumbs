import uiautomation as auto
from datetime import datetime
from typing import Optional

WIN32_APPS = {
    "outlook.exe": "Outlook",
    "explorer.exe": "File Explorer",
    "winword.exe": "Microsoft Word",
    "excel.exe": "Microsoft Excel",
    "powerpnt.exe": "PowerPoint",
    "notepad.exe": "Notepad",
    "mspaint.exe": "Paint",
    "calc.exe": "Calculator",
    "onenote.exe": "OneNote",
    "teams.exe": "Microsoft Teams",
    "thunderbird.exe": "Thunderbird",
}


def is_win32_app(app_name: str) -> bool:
    return app_name.lower() in WIN32_APPS


def get_app_friendly_name(app_name: str) -> str:
    return WIN32_APPS.get(app_name.lower(), app_name)


def build_uia_locator(element) -> str:
    if element.AutomationId:
        return f"AutomationId:{element.AutomationId}"
    if element.Name:
        return f"{element.ControlTypeName}:Name={element.Name}"
    if element.ClassName:
        return f"{element.ControlTypeName}:ClassName={element.ClassName}"
    return f"{element.ControlTypeName}:unknown"


def get_element_at_cursor() -> Optional[dict]:
    try:
        element = auto.ControlFromCursor()
        if not element:
            return None

        parents = []
        parent = element.GetParentControl()
        depth = 0
        while parent and depth < 3:
            parents.append({
                "name": parent.Name,
                "type": parent.ControlTypeName,
                "automation_id": parent.AutomationId
            })
            parent = parent.GetParentControl()
            depth += 1

        return {
            "timestamp": datetime.now().isoformat(),
            "name": element.Name,
            "control_type": element.ControlTypeName,
            "automation_id": element.AutomationId,
            "class_name": element.ClassName,
            "is_enabled": element.IsEnabled,
            "is_keyboard_focusable": element.IsKeyboardFocusable,
            "parent_chain": parents,
            "locator": build_uia_locator(element)
        }

    except Exception as e:
        print(f"[UIA] Error getting element: {e}")
        return None


def get_focused_element() -> Optional[dict]:
    try:
        element = auto.GetFocusedControl()
        if not element:
            return None

        return {
            "timestamp": datetime.now().isoformat(),
            "name": element.Name,
            "control_type": element.ControlTypeName,
            "automation_id": element.AutomationId,
            "class_name": element.ClassName,
            "locator": build_uia_locator(element)
        }

    except Exception as e:
        print(f"[UIA] Error getting focused element: {e}")
        return None
