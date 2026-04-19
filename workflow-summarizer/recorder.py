import win32gui
import win32process
import psutil
import mss
from datetime import datetime


def get_active_window() -> dict:
    hwnd = win32gui.GetForegroundWindow()
    title = win32gui.GetWindowText(hwnd)
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    try:
        app_name = psutil.Process(pid).name()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        app_name = "unknown"
    return {"app": app_name, "title": title, "hwnd": hwnd}


def capture_screenshot(output_dir: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"{output_dir}/{timestamp}.png"
    with mss.mss() as sct:
        sct.shot(output=filename)
    return filename
