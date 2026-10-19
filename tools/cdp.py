"""A small headless-Chromium driver over the DevTools protocol (Playwright's cached headless shell, no Playwright
library). One browser at a time; pages are local files.

    async with Chrome() as c:
        await c.size(1920, 1080); await c.transparent(); await c.goto(path)
        png = await c.shot()
"""
import asyncio
import base64
import itertools
import json
import os
import shutil
import socket
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path

from websockets.asyncio.client import connect

SHELL = os.environ.get('CHROME_SHELL') or os.path.expanduser('~/.cache/ms-playwright/chromium_headless_shell-1194/chrome-linux/headless_shell')


def free_port():
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


class Chrome:
    async def __aenter__(self):
        (Path(__file__).parent / 'tmp').mkdir(exist_ok=True)
        self.profile = tempfile.mkdtemp(prefix='cdp-', dir=Path(__file__).parent / 'tmp')
        port = free_port()
        self.proc = subprocess.Popen([SHELL, '--no-sandbox', '--disable-gpu', '--hide-scrollbars', '--mute-audio',
                                      f'--remote-debugging-port={port}', f'--user-data-dir={self.profile}',
                                      '--allow-file-access-from-files', '--force-color-profile=srgb',
                                      '--disable-features=PaintHolding', 'about:blank'],
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        url = None
        for _ in range(100):
            try:
                with urllib.request.urlopen(f'http://127.0.0.1:{port}/json/version', timeout=1) as r:
                    url = json.load(r)['webSocketDebuggerUrl']
                    break
            except OSError:
                time.sleep(0.1)
        if not url:
            raise RuntimeError('headless shell did not start')
        self.ws = await connect(url, max_size=None)
        self.ids, self.pending, self.events = itertools.count(1), {}, []
        self.reader = asyncio.create_task(self._read())
        t = await self.call('Target.createTarget', url='about:blank', session=None)
        a = await self.call('Target.attachToTarget', targetId=t['targetId'], flatten=True, session=None)
        self.session = a['sessionId']
        await self.call('Page.enable')
        await self.call('Runtime.enable')
        return self

    async def __aexit__(self, *exc):
        try:
            await self.ws.close()
        finally:
            self.reader.cancel()
            self.proc.terminate()
            try:
                self.proc.wait(5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
            shutil.rmtree(self.profile, ignore_errors=True)

    async def _read(self):
        async for msg in self.ws:
            m = json.loads(msg)
            if 'id' in m:
                fut = self.pending.pop(m['id'], None)
                if fut and not fut.done():
                    fut.set_result(m)
            else:
                self.events.append(m)

    async def call(self, method, session='page', **params):
        i = next(self.ids)
        fut = asyncio.get_running_loop().create_future()
        self.pending[i] = fut
        msg = {'id': i, 'method': method, 'params': params}
        if session == 'page':
            msg['sessionId'] = self.session
        await self.ws.send(json.dumps(msg))
        r = await asyncio.wait_for(fut, 60)
        if 'error' in r:
            raise RuntimeError(f"{method}: {r['error']}")
        return r.get('result', {})

    async def size(self, w, h, dpr=1):
        await self.call('Emulation.setDeviceMetricsOverride', width=w, height=h, deviceScaleFactor=dpr, mobile=False)

    async def transparent(self, on=True):
        await self.call('Emulation.setDefaultBackgroundColorOverride',
                        **({'color': {'r': 0, 'g': 0, 'b': 0, 'a': 0}} if on else {}))

    async def goto(self, path):
        self.events.clear()
        await self.call('Page.navigate', url=Path(path).resolve().as_uri())
        for _ in range(600):
            if any(e.get('method') == 'Page.loadEventFired' for e in self.events):
                break
            await asyncio.sleep(0.02)
        await self.eval('document.fonts.ready.then(() => true)', wait=True)
        errors = [e for e in self.events if e.get('method') in ('Runtime.exceptionThrown',)
                  or (e.get('method') == 'Runtime.consoleAPICalled' and e['params'].get('type') == 'error')]
        if errors:
            raise RuntimeError(f'page errors in {path}: {json.dumps(errors)[:800]}')

    async def eval(self, expr, wait=False):
        r = await self.call('Runtime.evaluate', expression=expr, awaitPromise=wait, returnByValue=True)
        if 'exceptionDetails' in r:
            raise RuntimeError(f"eval {expr[:80]}: {r['exceptionDetails']}")
        return r.get('result', {}).get('value')

    async def shot(self, out=None):
        r = await self.call('Page.captureScreenshot', format='png', fromSurface=True)
        data = base64.b64decode(r['data'])
        if out:
            Path(out).write_bytes(data)
        return data
