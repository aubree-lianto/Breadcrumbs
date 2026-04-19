from pynput import mouse
from uia_capture import get_element_at_cursor, is_win32_app
from hooks import get_window_info
import win32gui
import ctypes
import queue
from datetime import datetime

click_event_queue = queue.Queue()
_click_listener = None
_com_initialized = False


def ensure_com():
    global _com_initialized
    if not _com_initialized:
        ctypes.windll.ole32.CoInitialize(0)
        _com_initialized = True


def on_click(x, y, button, pressed):
    if not pressed:
        return

    ensure_com()
    hwnd = win32gui.GetForegroundWindow()
    window_info = get_window_info(hwnd)

    if not window_info:
        return

    app_name = window_info["app"]

    if is_win32_app(app_name):
        element = get_element_at_cursor()

        event = {
            "type": "click",
            "timestamp": datetime.now().isoformat(),
            "x": x,
            "y": y,
            "button": str(button),
            "app": app_name,
            "window_title": window_info["title"],
            "source": "uia",
            "element": element
        }

        click_event_queue.put(event)

        if element:
            name = element.get('name', 'unnamed') or 'unnamed'
            print(f"[UIA CLICK] {element['control_type']}: {name[:30]}")


def start_click_hook():
    global _click_listener
    _click_listener = mouse.Listener(on_click=on_click)
    _click_listener.start()
    print("[HOOK] Global click hook active (UIA for Win32 apps)")
    return _click_listener


def stop_click_hook():
    global _click_listener
    if _click_listener:
        _click_listener.stop()
        _click_listener = None


def get_click_events() -> list:
    events = []
    while not click_event_queue.empty():
        try:
            events.append(click_event_queue.get_nowait())
        except queue.Empty:
            break
    return events


def clear_click_events():
    while not click_event_queue.empty():
        try:
            click_event_queue.get_nowait()
        except queue.Empty:
            break
