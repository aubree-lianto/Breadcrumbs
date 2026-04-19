import sys
sys.path.insert(0, '.')

from electron_launcher import list_electron_apps, launch_with_debug

print("Known Electron apps:")
for app in list_electron_apps():
    status = "RUNNING" if app["running"] else "stopped"
    found = "found" if app["found"] else "NOT FOUND"
    print(f"  {app['app']}: {status}, {found}, port {app['port']}")

print("\nLaunching VS Code with debug port...")
result = launch_with_debug("code.exe")
print(f"Launch result: {result}")
