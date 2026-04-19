import asyncio
import sys
sys.path.insert(0, '.')

from electron_capture import capture_electron_events

async def main():
    print("Capturing VS Code clicks for 15 seconds — click around in VS Code...")
    events = await capture_electron_events(port=9222, duration=15)
    print(f"\nCaptured {len(events)} events")
    for e in events:
        print(e)

asyncio.run(main())
