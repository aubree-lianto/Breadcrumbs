import sys
sys.path.insert(0, '.')

from hooks import start_event_hook, get_next_event
import time

start_event_hook()
time.sleep(0.5)
print("Switch between apps...")

for _ in range(10):
    event = get_next_event(timeout=5)
    if event:
        print(f"[SWITCH] {event['app']} - {event['title'][:50]}")
