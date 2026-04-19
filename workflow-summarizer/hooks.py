import ctypes
from ctypes import wintypes
import win32gui
import win32process
import psutil
import threading
import queue
from datetime import datetime

# Event constants
EVENT_SYSTEM_FOREGROUND = 0x0003
WINEVENT_OUTOFCONTEXT = 0x0000
WINEVENT_SKIPOWNPROCESS = 0x0002

# Queue for passing events to main thread
event_queue = queue.Queue()

# Callback type
WinEventProcType = ctypes.WINFUNCTYPE(
    None,
    wintypes.HANDLE,
    wintypes.DWORD,
    wintypes.HWND,
    wintypes.LONG,
    wintypes.LONG,
    wintypes.DWORD,
    wintypes.DWORD
)


def get_window_info(hwnd):
    try:
        title = win32gui.GetWindowText(hwnd)
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        process = psutil.Process(pid)
        app_name = process.name()
        exe_path = process.exe()
        return {
            "hwnd": hwnd,
            "title": title,
            "app": app_name,
            "exe_path": exe_path,
            "pid": pid,
            "timestamp": datetime.now().isoformat()
        }
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None


def _win_event_callback(hWinEventHook, event, hwnd, idObject, idChild, dwEventThread, dwmsEventTime):
    if event == EVENT_SYSTEM_FOREGROUND and hwnd:
        info = get_window_info(hwnd)
        if info:
            event_queue.put(info)


# Keep callback reference alive (prevent garbage collection)
_callback = WinEventProcType(_win_event_callback)


def start_event_hook():
    def hook_thread():
        user32 = ctypes.windll.user32
        ole32 = ctypes.windll.ole32

        ole32.CoInitialize(0)

        hook = user32.SetWinEventHook(
            EVENT_SYSTEM_FOREGROUND,
            EVENT_SYSTEM_FOREGROUND,
            0,
            _callback,
            0,
            0,
            WINEVENT_OUTOFCONTEXT | WINEVENT_SKIPOWNPROCESS
        )

        if not hook:
            print("[ERROR] Failed to set up Windows event hook")
            return

        print("[HOOK] Windows event hook active")

        msg = wintypes.MSG()
        while user32.GetMessageW(ctypes.byref(msg), 0, 0, 0) != 0:
            user32.TranslateMessageW(msg)
            user32.DispatchMessageW(msg)

        user32.UnhookWinEvent(hook)
        ole32.CoUninitialize()

    thread = threading.Thread(target=hook_thread, daemon=True)
    thread.start()
    return thread


def get_next_event(timeout=None):
    try:
        return event_queue.get(timeout=timeout)
    except queue.Empty:
        return None


def clear_events():
    while not event_queue.empty():
        try:
            event_queue.get_nowait()
        except queue.Empty:
            break
