import subprocess
import os
import glob
import time
import psutil

# Known Electron apps and their debug ports
ELECTRON_APPS = {
    "code.exe": {
        "name": "VS Code",
        "port": 9222,
        "paths": [
            r"C:\Users\{user}\AppData\Local\Programs\Microsoft VS Code\Code.exe",
            r"C:\Program Files\Microsoft VS Code\Code.exe"
        ]
    },
    "slack.exe": {
        "name": "Slack",
        "port": 9223,
        "paths": [
            r"C:\Users\{user}\AppData\Local\slack\slack.exe"
        ]
    },
    "discord.exe": {
        "name": "Discord",
        "port": 9224,
        "paths": [
            r"C:\Users\{user}\AppData\Local\Discord\app-*\Discord.exe"
        ]
    },
    "notion.exe": {
        "name": "Notion",
        "port": 9225,
        "paths": [
            r"C:\Users\{user}\AppData\Local\Programs\Notion\Notion.exe"
        ]
    }
}


def get_user() -> str:
    return os.environ.get("USERNAME", "User")


def find_executable(app_key: str) -> str:
    if app_key not in ELECTRON_APPS:
        return None

    user = get_user()

    for path_template in ELECTRON_APPS[app_key]["paths"]:
        path = path_template.replace("{user}", user)

        if "*" in path:
            matches = glob.glob(path)
            if matches:
                return matches[0]
        elif os.path.exists(path):
            return path

    return None


def is_app_running(app_name: str) -> tuple:
    for proc in psutil.process_iter(['name', 'pid']):
        if proc.info['name'].lower() == app_name.lower():
            return True, proc.info['pid']
    return False, None


def kill_app(app_name: str):
    for proc in psutil.process_iter(['name', 'pid']):
        if proc.info['name'].lower() == app_name.lower():
            try:
                proc.kill()
                print(f"[KILLED] {app_name} (PID {proc.info['pid']})")
            except psutil.AccessDenied:
                print(f"[ERROR] Cannot kill {app_name} - access denied")


def launch_with_debug(app_key: str, kill_existing: bool = True) -> dict:
    if app_key not in ELECTRON_APPS:
        return {"success": False, "error": f"Unknown app: {app_key}"}

    config = ELECTRON_APPS[app_key]
    exe_path = find_executable(app_key)

    if not exe_path:
        return {"success": False, "error": f"Could not find {config['name']} executable"}

    if kill_existing:
        running, pid = is_app_running(app_key)
        if running:
            print(f"[INFO] Killing existing {config['name']}...")
            kill_app(app_key)
            time.sleep(2)

    port = config["port"]
    cmd = [exe_path, f"--remote-debugging-port={port}"]

    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.DETACHED_PROCESS
        )

        print(f"[LAUNCHED] {config['name']} with debug port {port}")

        return {
            "success": True,
            "app": config["name"],
            "port": port,
            "pid": process.pid,
            "debug_url": f"http://localhost:{port}"
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


def get_debug_port(app_name: str) -> int:
    app_key = app_name.lower()
    if app_key in ELECTRON_APPS:
        return ELECTRON_APPS[app_key]["port"]
    return None


def list_electron_apps() -> list:
    results = []
    for app_key, config in ELECTRON_APPS.items():
        running, pid = is_app_running(app_key)
        exe_path = find_executable(app_key)
        results.append({
            "app": config["name"],
            "key": app_key,
            "port": config["port"],
            "running": running,
            "pid": pid,
            "found": exe_path is not None
        })
    return results
