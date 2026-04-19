import sys
sys.path.insert(0, '.')

from click_hook import start_click_hook, get_click_events
import time

start_click_hook()
print("Click around in Outlook or other Win32 apps...")
print("Press Ctrl+C to stop\n")

try:
    while True:
        events = get_click_events()
        for e in events:
            elem = e.get('element') or {}
            name = elem.get('name', 'unknown') or 'unknown'
            ctrl = elem.get('control_type', '?')
            print(f"[CLICK] {e['app']} - {name[:40]} ({ctrl})")
        time.sleep(0.5)
except KeyboardInterrupt:
    print("\nDone")
