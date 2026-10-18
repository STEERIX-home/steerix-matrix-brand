"""Render the animation pages frame by frame in headless Chromium (renderAt(ms), transparent background), then
encode: MP4 on black (H.264; loaders repeated to ~10 s), MOV with alpha (ProRes 4444, one cycle) and GIF on black
(one cycle, looping). A contact sheet of each lands in tools/check.

    ~/office-film-v5/dish/.venv/bin/python render.py OUT_DIR [job ...]
"""
import asyncio
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlencode

import anim as A
from cdp import Chrome

KIT = Path(__file__).parent
FF = 'ffmpeg'
# key: (dir, page, query, viewport, dpr, fps, frames, out name, gif width, mp4 repeats)
JOBS = {
    's2m': (1, 'steerix-to-matrix.html', {}, (1920, 1080), 1, 60, 156, 'steerix-to-matrix', 960, 1),
    'm2s': (2, 'matrix-to-steerix.html', {}, (1920, 1080), 1, 60, 156, 'matrix-to-steerix', 960, 1),
    's2m-green': (1, 'steerix-to-matrix.html', {'color': 'green'}, (1920, 1080), 1, 60, 156, 'steerix-to-matrix-green-x', 960, 1),
    'm2s-green': (2, 'matrix-to-steerix.html', {'color': 'green'}, (1920, 1080), 1, 60, 156, 'matrix-to-steerix-green-x', 960, 1),
    'x2s-cyan': (3, 'loading-x-to-steerix.html', {'color': 'cyan'}, (1080, 1080), 1, 50, 181, 'loading-x-to-steerix-cyan', 480, 3),
    'x2s-white': (3, 'loading-x-to-steerix.html', {'color': 'white'}, (1080, 1080), 1, 50, 181, 'loading-x-to-steerix-white', 480, 3),
    'x2s-green': (3, 'loading-x-to-steerix.html', {'color': 'green'}, (1080, 1080), 1, 50, 181, 'loading-x-to-steerix-green', 480, 3),
    'xturn-color': (4, 'loading-matrix-x-turn.html', {'color': 'cyan'}, (1440, 360), 1, 50, 181, 'loading-matrix-x-turn-color', 720, 3),
    'xturn-white': (4, 'loading-matrix-x-turn.html', {'color': 'white'}, (1440, 360), 1, 50, 181, 'loading-matrix-x-turn-white', 720, 3),
    'xturn-green': (4, 'loading-matrix-x-turn.html', {'color': 'green'}, (1440, 360), 1, 50, 181, 'loading-matrix-x-turn-green', 720, 3),
    'steerix-green': (5, 'loading-steerix-spin.html', {'color': 'green'}, (1080, 1080), 1, 50, 90, 'loading-steerix-spin-green', 480, 6),
    'steerix-white': (5, 'loading-steerix-spin.html', {'color': 'white'}, (1080, 1080), 1, 50, 90, 'loading-steerix-spin-white', 480, 6),
    'steerix-rain': (5, 'loading-steerix-code-rain.html', {}, (320, 320), 3.375, 50, 90, 'loading-steerix-code-rain', 480, 6),
}


def run(args):
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


async def frames(c, out, key):
    d, html, query, (w, h), dpr, fps, n, name, *_ = JOBS[key]
    fdir = KIT / 'tmp/frames' / key
    shutil.rmtree(fdir, ignore_errors=True)
    fdir.mkdir(parents=True)
    await c.size(w, h, dpr)
    await c.transparent(True)
    q = urlencode({'capture': 1, 'bg': 'transparent', **query})
    c.events.clear()
    await c.call('Page.navigate', url=(out / A.DIRS[d] / html).resolve().as_uri() + '?' + q)
    for _ in range(600):
        if any(e.get('method') == 'Page.loadEventFired' for e in c.events):
            break
        await asyncio.sleep(0.02)
    await c.eval('document.fonts.ready.then(() => document.fonts.load(\'18px "IBM Plex Mono"\')).then(() => true)', wait=True)
    errs = [e for e in c.events if e.get('method') == 'Runtime.exceptionThrown']
    if errs:
        raise RuntimeError(f'{key}: {errs[0]}')
    for i in range(n):
        await c.eval(f'renderAt({i * 1000 / fps})')
        await c.eval('new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(() => r(true))))', wait=True)
        await c.shot(fdir / f'{i:04d}.png')
    return fdir


def encode(out, key, fdir):
    d, html, query, (w, h), dpr, fps, n, name, gif_w, reps = JOBS[key]
    W, H = round(w * dpr), round(h * dpr)
    dest = out / A.DIRS[d]
    src = ['-framerate', str(fps), '-i', str(fdir / '%04d.png')]
    black = f'color=c=black:s={W}x{H}:r={fps}[bg];[bg][0:v]overlay=shortest=1:format=auto'
    loop = ['-stream_loop', str(reps - 1)] if reps > 1 else []
    run([FF, '-y', '-v', 'error', *loop, *src, '-filter_complex', black + ',format=yuv420p',
         '-c:v', 'libx264', '-crf', '14', '-preset', 'slow', '-movflags', '+faststart', str(dest / f'{name}.mp4')])
    run([FF, '-y', '-v', 'error', *src, '-c:v', 'prores_ks', '-profile:v', '4444', '-pix_fmt', 'yuva444p10le',
         '-vendor', 'apl0', str(dest / f'{name}-transparent.mov')])
    gif_fps = 30 if fps == 60 else fps
    hold = ['-final_delay', '150'] if reps == 1 else []
    run([FF, '-y', '-v', 'error', *src, '-filter_complex',
         black + f',fps={gif_fps},scale={gif_w}:-2:flags=lanczos,split[a][b];[a]palettegen=stats_mode=full[p];'
         '[b][p]paletteuse=dither=sierra2_4a', '-loop', '0', *hold, str(dest / f'{name}.gif')])
    # contact sheet for checking
    pick = max(1, n // 12)
    run([FF, '-y', '-v', 'error', *src, '-filter_complex',
         black + f",select='not(mod(n\\,{pick}))',scale=480:-2,tile=4x3", '-frames:v', '1', str(KIT / 'check' / f'sheet-{key}.jpg')])


async def main(out, keys):
    async with Chrome() as c:
        for key in keys:
            fdir = await frames(c, out, key)
            encode(out, key, fdir)
            print(key, 'ok', flush=True)


if __name__ == '__main__':
    out = Path(sys.argv[1]).expanduser()
    asyncio.run(main(out, sys.argv[2:] or list(JOBS)))
