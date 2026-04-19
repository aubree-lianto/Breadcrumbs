import asyncio
import websockets
import json
import aiohttp


class ElectronCapture:
    def __init__(self, port: int):
        self.port = port
        self.ws = None
        self.message_id = 0

    async def connect(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://localhost:{self.port}/json") as resp:
                targets = await resp.json(content_type=None)

        page_target = next((t for t in targets if t.get("type") == "page"), None)

        if not page_target:
            raise Exception("No page target found")

        ws_url = page_target["webSocketDebuggerUrl"]
        self.ws = await websockets.connect(ws_url)
        print(f"[ELECTRON] Connected to {page_target.get('title', 'unknown')[:50]}")

        await self._send("DOM.enable")
        await self._send("Runtime.enable")
        return True

    async def _send(self, method: str, params: dict = None):
        self.message_id += 1
        msg = {"id": self.message_id, "method": method, "params": params or {}}
        await self.ws.send(json.dumps(msg))

        while True:
            response = await asyncio.wait_for(self.ws.recv(), timeout=5.0)
            data = json.loads(response)
            if data.get("id") == self.message_id:
                return data.get("result")

    async def inject_click_listener(self):
        script = r"""
        (function() {
            if (window.__breadcrumbsInjected) return 'already injected';
            window.__breadcrumbsInjected = true;
            window.__breadcrumbsEvents = [];

            function getSelector(el) {
                if (el.id) return '#' + el.id;
                if (el.getAttribute('data-testid')) return '[data-testid="' + el.getAttribute('data-testid') + '"]';
                if (el.getAttribute('aria-label')) return '[aria-label="' + el.getAttribute('aria-label') + '"]';
                let path = [];
                let current = el;
                while (current && current !== document.body && path.length < 4) {
                    let selector = current.tagName.toLowerCase();
                    if (current.className && typeof current.className === 'string') {
                        const cls = current.className.trim().split(/\s+/)[0];
                        if (cls) selector += '.' + cls;
                    }
                    path.unshift(selector);
                    current = current.parentElement;
                }
                return path.join(' > ');
            }

            document.addEventListener('click', function(e) {
                window.__breadcrumbsEvents.push({
                    type: 'click',
                    timestamp: Date.now(),
                    selector: getSelector(e.target),
                    tag: e.target.tagName.toLowerCase(),
                    text: (e.target.innerText || '').slice(0, 50),
                    x: e.clientX,
                    y: e.clientY
                });
            }, true);

            document.addEventListener('keydown', function(e) {
                if (['Enter', 'Tab', 'Escape'].includes(e.key)) {
                    window.__breadcrumbsEvents.push({
                        type: 'keypress',
                        timestamp: Date.now(),
                        key: e.key,
                        selector: getSelector(e.target),
                        tag: e.target.tagName.toLowerCase()
                    });
                }
            }, true);

            return 'injected';
        })();
        """

        result = await self._send("Runtime.evaluate", {
            "expression": script,
            "returnByValue": True
        })
        status = result.get("result", {}).get("value", "unknown")
        print(f"[ELECTRON] Click listener: {status}")
        return status

    async def get_events(self) -> list:
        result = await self._send("Runtime.evaluate", {
            "expression": "window.__breadcrumbsEvents ? window.__breadcrumbsEvents.splice(0) : []",
            "returnByValue": True
        })
        return result.get("result", {}).get("value", [])

    async def close(self):
        if self.ws:
            await self.ws.close()
            self.ws = None


async def capture_electron_events(port: int, duration: int = 10):
    capture = ElectronCapture(port)
    try:
        await capture.connect()
        await capture.inject_click_listener()
        print(f"[ELECTRON] Capturing for {duration} seconds...")

        all_events = []
        for _ in range(duration * 2):
            await asyncio.sleep(0.5)
            events = await capture.get_events()
            if events:
                all_events.extend(events)
                for e in events:
                    print(f"  [{e['type']}] {e.get('selector', '')} - {e.get('text', e.get('key', ''))}")

        return all_events
    finally:
        await capture.close()


def get_electron_events_sync(port: int) -> list:
    async def _get():
        capture = ElectronCapture(port)
        try:
            await capture.connect()
            await capture.inject_click_listener()
            return await capture.get_events()
        except Exception as e:
            print(f"[ELECTRON] Error: {e}")
            return []
        finally:
            await capture.close()

    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            raise RuntimeError
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(_get())
