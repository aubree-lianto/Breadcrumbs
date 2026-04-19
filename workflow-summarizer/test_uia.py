import sys
sys.path.insert(0, '.')

from uia_capture import get_element_at_cursor
import time

print("Move cursor over UI elements in Outlook or any Win32 app...")
print("Press Ctrl+C to stop\n")

try:
    while True:
        element = get_element_at_cursor()
        if element and element.get('name'):
            print(f"[CURSOR] {element['control_type']}: {element['name'][:50]}")
            print(f"         Locator: {element['locator']}")
        time.sleep(1)
except KeyboardInterrupt:
    print("\nDone")
