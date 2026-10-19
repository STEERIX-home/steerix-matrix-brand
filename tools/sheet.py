"""브랜드시트.html: every logo, colour, font and animation in the folder on one page, with links to the files.
Self-contained apart from the folder's own files (relative links), so it works opened straight from the Desktop.

    python3 sheet.py OUT_DIR
"""
import sys
from pathlib import Path
from urllib.parse import quote

import anim as A
import logos as L
import robotsim as R
import shapes as S

CSS = '''
:root { --bg: #050808; --panel: #0d1414; --raised: #121c1c; --line: #1f2d2c; --fg: #e6efec; --muted: #8aa3a3;
  --green: #00db89; --light: #f4f7f6; }
@font-face { font-family: "IBM Plex Sans"; src: url("4-%ED%8F%B0%ED%8A%B8/UI%20%EA%B8%80%EA%BC%B4%20(IBM%20Plex)/IBMPlexSans-Regular-Latin.ttf"); font-weight: 400; }
@font-face { font-family: "IBM Plex Sans"; src: url("4-%ED%8F%B0%ED%8A%B8/UI%20%EA%B8%80%EA%BC%B4%20(IBM%20Plex)/IBMPlexSans-SemiBold-Latin.ttf"); font-weight: 600; }
@font-face { font-family: "Inter Tight"; src: url("4-%ED%8F%B0%ED%8A%B8/RobotSim%20%EA%B8%80%EA%BC%B4%20(Inter%20Tight,%20JetBrains%20Mono)/InterTight[wght].ttf"); font-weight: 100 900; }
@font-face { font-family: "JetBrains Mono"; src: url("4-%ED%8F%B0%ED%8A%B8/RobotSim%20%EA%B8%80%EA%BC%B4%20(Inter%20Tight,%20JetBrains%20Mono)/JetBrainsMono[wght].ttf"); font-weight: 100 800; }
@font-face { font-family: "STEERIX Logo"; src: url("4-%ED%8F%B0%ED%8A%B8/STEERIX-Logo-Regular.ttf"); }
@font-face { font-family: "MATRIX Logo"; src: url("4-%ED%8F%B0%ED%8A%B8/MATRIX-Logo-Regular.ttf"); }
* { box-sizing: border-box; }
html, body { margin: 0; background: var(--bg); color: var(--fg); }
body { font: 15px/1.55 "IBM Plex Sans", system-ui, -apple-system, "Segoe UI", "Apple SD Gothic Neo", "Malgun Gothic", sans-serif; }
main { max-width: 1200px; margin: 0 auto; padding: 40px 16px 80px; }
header { display: flex; flex-wrap: wrap; gap: 24px; align-items: flex-end; justify-content: space-between; margin-bottom: 40px; }
header img { height: 36px; display: block; }
h1 { font-size: 28px; font-weight: 600; margin: 16px 0 4px; letter-spacing: -0.01em; }
h2 { font-size: 20px; font-weight: 600; margin: 56px 0 6px; }
h3 { font-size: 16px; font-weight: 600; margin: 0; }
p.lead, .muted { color: var(--muted); }
p.lead { margin: 0; max-width: 680px; }
.grid { display: grid; gap: 16px; grid-template-columns: repeat(auto-fill, minmax(min(100%, 340px), 1fr)); margin-top: 16px; }
.grid.wide { grid-template-columns: repeat(auto-fill, minmax(min(100%, 520px), 1fr)); }
.card { background: var(--panel); border: 1px solid var(--line); border-radius: 10px; overflow: hidden; display: flex; flex-direction: column; }
.card .body { padding: 14px 16px 16px; display: flex; flex-direction: column; gap: 8px; }
.card .body p { margin: 0; font-size: 13px; }
.view { display: flex; align-items: center; justify-content: center; padding: 28px; min-height: 160px; background: #000; }
.view.light { background: var(--light); }
.view.pair { display: grid; grid-template-columns: 1fr 1fr; padding: 0; }
.view.pair > div { display: flex; align-items: center; justify-content: center; padding: 24px; min-height: 140px; }
.view img, .view video { max-width: 100%; max-height: 120px; display: block; }
.view.anim img, .view.anim video { max-height: 220px; }
.view.anim img.full { max-height: none; width: 100%; margin: 0; }
.view.anim { padding: 0; min-height: 200px; }
.view.anim img { margin: 24px; width: 180px; }
.view.anim img.wide { width: min(90%, 520px); }
.links { display: flex; flex-wrap: wrap; gap: 6px; }
.links a { font-size: 12px; color: var(--fg); text-decoration: none; border: 1px solid var(--line); background: var(--raised);
  border-radius: 999px; padding: 3px 10px; white-space: nowrap; }
.links a:hover { border-color: var(--green); }
.links a.main { border-color: var(--green); color: var(--green); }
.swatches { display: grid; gap: 12px; grid-template-columns: repeat(auto-fill, minmax(min(100%, 170px), 1fr)); margin-top: 16px; }
.swatch { border: 1px solid var(--line); border-radius: 10px; overflow: hidden; background: var(--panel); }
.swatch div { height: 64px; }
.swatch p { margin: 0; padding: 8px 12px 10px; font-size: 13px; }
.swatch code { font-family: "IBM Plex Mono", ui-monospace, monospace; color: var(--fg); }
.tester { background: var(--panel); border: 1px solid var(--line); border-radius: 10px; padding: 16px; margin-top: 16px; }
.tester input { width: 100%; font: inherit; color: var(--fg); background: #000; border: 1px solid var(--line); border-radius: 6px; padding: 8px 10px; }
.tester .out { font-size: clamp(32px, 7vw, 72px); line-height: 1.25; margin: 16px 0 4px; overflow-wrap: anywhere; }
.tester .s { font-family: "STEERIX Logo"; }
.tester .m { font-family: "MATRIX Logo"; }
.rs { background: #07090b; border: 1px solid var(--line); border-radius: 10px; padding: 20px; margin-top: 16px; }
.rs .h { font-family: "Inter Tight"; font-weight: 800; font-size: clamp(30px, 5vw, 54px); line-height: 1.05; letter-spacing: -0.03em; color: #e9eff1; }
.rs .h span { color: #5ef2c2; }
.rs .b { font-family: "Inter Tight"; font-size: 17px; color: #8d9ca3; margin-top: 12px; }
.rs .m { font-family: "JetBrains Mono"; font-size: 13px; letter-spacing: 0.08em; color: #5ef2c2; margin-top: 14px; }
button.replay { font: inherit; font-size: 12px; color: var(--fg); background: var(--raised); border: 1px solid var(--line);
  border-radius: 999px; padding: 3px 10px; cursor: pointer; }
footer { margin-top: 64px; color: var(--muted); font-size: 13px; border-top: 1px solid var(--line); padding-top: 16px; }
'''


A_COLOURWAYS = {k: list(v) for k, v in S.COLOURS.items()}
CW_LABEL = {'white': '흰색', 'black': '검정', 'green': '초록', 'green-x': '초록 X', 'black-green-x': '검정 + 초록 X',
            'mint': '민트 (사이트)', 'black-mint': '검정 + 민트 마크'}


def robotsim_card(name, title, note, previews):
    """RobotSim files: PNG and SVG in every colourway, PDF and AI for all but white (no EPS: the mark has transparency)."""
    d = Path(R.DIRS[name])
    ways = R.LOGOS[name][1]
    files = [(f'PNG {CW_LABEL[cw]}', d / f'{name}-{cw}.png', cw == ways[0]) for cw in ways]
    files += [(f'SVG {CW_LABEL[cw]}', d / f'{name}-{cw}.svg', False) for cw in ways]
    for cw in ways:
        if cw != 'white':
            files += [(f'AI {CW_LABEL[cw]}', d / f'{name}-{cw}.ai', False), (f'PDF {CW_LABEL[cw]}', d / f'{name}-{cw}.pdf', False)]
    view = '<div class="view pair">' + ''.join(
        f'<div style="background:{bg}"><img src="{href(d / f"{name}-{cw}.png")}" alt="{title} {CW_LABEL[cw]}"></div>'
        for cw, bg in previews) + '</div>'
    return f'<article class="card">{view}<div class="body"><h3>{title}</h3><p class="muted">{note}</p>{links(files)}</div></article>'


def href(path):
    return quote(str(path))


def links(items):
    return '<div class="links">' + ''.join(f'<a{" class=\"main\"" if main else ""} href="{href(p)}">{label}</a>'
                                           for label, p, main in items) + '</div>'


def logo_card(name, title, note, previews, extra=(), only=None):
    d = Path(L.DIRS[name])
    files = []
    ways = [cw for cw in A_COLOURWAYS[name] if only is None or cw in only]
    for cw in ways:
        files.append((f'PNG {CW_LABEL[cw]}', d / f'{name}-{cw}.png', cw == ways[0]))
    for cw in ways:
        files.append((f'SVG {CW_LABEL[cw]}', d / f'{name}-{cw}.svg', False))
    for cw in ways:
        if cw == 'white':
            continue
        stem = name if cw == 'black' else f'{name}-{cw}'
        tag = '' if cw == 'black' else f' {CW_LABEL[cw]}'
        files += [(f'AI{tag}', d / f'{stem}.ai', False), (f'PDF{tag}', d / f'{stem}.pdf', False), (f'EPS{tag}', d / f'{stem}.eps', False)]
    files += list(extra)
    view = '<div class="view pair">' + ''.join(
        f'<div style="background:{bg}"><img src="{href(d / f"{name}-{cw}.png")}" alt="{title} {CW_LABEL[cw]}"></div>'
        for cw, bg in previews) + '</div>'
    return f'<article class="card">{view}<div class="body"><h3>{title}</h3><p class="muted">{note}</p>{links(files)}</div></article>'



def anim_card(k, title, note, preview, files, wide=False):
    d = Path(A.DIRS[k])
    return (f'<article class="card"><div class="view anim">{preview}</div><div class="body"><h3>{title}</h3>'
            f'<p class="muted">{note}</p>{links([(lab, d / f, main) for lab, f, main in files])}</div></article>')


def video(path, cls=''):
    """The GIF as the preview: it plays in every browser (an H.264 MP4 does not play in Chromium builds)."""
    return f'<img class="{cls}" src="{href(path.with_suffix(".gif"))}" alt="">'


def build():
    D = {k: Path(v) for k, v in A.DIRS.items()}
    steerix = ''.join([
        logo_card('steerix-logo', '로고 (심볼 + 글자)', '기본 로고. 흰색은 어두운 배경, 검정은 밝은 배경용입니다.',
                  [('white', '#000'), ('black', '#f4f7f6')]),
        logo_card('steerix-symbol', '심볼 (그림만)', '앱 아이콘과 같은 모양. 초록은 앱의 STEERIX 색(#00DC7D)입니다.',
                  [('white', '#000'), ('green', '#000')],
                  extra=[('앱 아이콘 1024px', Path(L.DIRS['steerix-symbol']) / 'steerix-app-icon-1024.png', False)]),
        logo_card('steerix-wordmark', '글자만', 'STEERIX 글자. 폰트로 쓰려면 아래 STEERIX Logo 폰트를 설치하세요.',
                  [('white', '#000'), ('black', '#f4f7f6')]),
    ])
    matrix = ''.join([
        logo_card('matrix-logo', '로고 (MATRIX 전체 글자)', 'MATRI 글자와 X 마크. 초록 X 버전은 앱 화면 색(글자 #E6EFEC, X #00DB89)입니다.',
                  [('white', '#000'), ('green-x', '#000')]),
        logo_card('matrix-x', 'X 로고만', 'MATRIX의 X 마크(파비콘과 같은 모양). 초록은 #00DB89입니다.',
                  [('white', '#000'), ('green', '#000')]),
    ])
    matrix_light = logo_card('matrix-logo', '로고 — 밝은 배경', '검정 글자, 또는 검정 글자 + 초록 X.',
                             [('black', '#f4f7f6'), ('black-green-x', '#f4f7f6')], only=('black', 'black-green-x'))
    robotsim = ''.join([
        robotsim_card('robotsim-logo', '로고 (마크 + RobotSim)', '사이트 머리글과 같은 로고. 민트는 사이트 그대로(마크 #5EF2C2, 글자 #E9EFF1)이고 어두운 배경용입니다.',
                      [('mint', '#07090b'), ('black-mint', '#f4f7f6')]),
        robotsim_card('robotsim-logo-by-steerix', '로고 + by Steerix', '사이트 머리글 전체(by Steerix #8D9CA3). 데스크톱 머리글, 영상 엔드카드, 공유 이미지에 씁니다.',
                      [('mint', '#07090b'), ('black-mint', '#f4f7f6')]),
        robotsim_card('robotsim-mark', '큐브 마크', '파비콘과 같은 모양. 옆면은 45% 투명입니다.', [('mint', '#07090b'), ('white', '#000')]),
    ])
    rs_colours = [('#5EF2C2', 'RobotSim 민트', '마크, 강조, 버튼'), ('#E9EFF1', '글자', 'RobotSim, 제목'),
                  ('#8D9CA3', '보조 글자', 'by Steerix, 설명'), ('#07090B', '배경', '사이트 바탕')]
    rs_sw = ''.join(f'<div class="swatch"><div style="background:{c}"></div><p><code>{c}</code><br>{n}<br><span class="muted">{u}</span></p></div>'
                    for c, n, u in rs_colours)
    rs_fonts = Path('4-폰트') / 'RobotSim 글꼴 (Inter Tight, JetBrains Mono)'
    rs_font_links = links([('Inter Tight (TTF, 가변)', rs_fonts / 'InterTight[wght].ttf', True),
                           ('JetBrains Mono (TTF, 가변)', rs_fonts / 'JetBrainsMono[wght].ttf', True),
                           ('OFL 라이선스 (Inter Tight)', rs_fonts / 'InterTight-OFL.txt', False),
                           ('OFL 라이선스 (JetBrains Mono)', rs_fonts / 'JetBrainsMono-OFL.txt', False)])
    colours = [('#FFFFFF', '로고 흰색', '어두운 배경의 로고'), ('#000000', '로고 검정 · 인트로 배경', '밝은 배경의 로고'),
               ('#00DB89', 'MATRIX X 초록', 'ready · 파비콘'), ('#00DC7D', 'STEERIX 초록', '앱의 STEERIX 심볼'),
               ('#E6EFEC', 'MATRIX 글자 (앱)', '앱 헤더의 MATRI'), ('#53C1DB', '하늘색 · 작업 중', '앱 로딩 아이콘'),
               ('#F5B536', '주의', 'attention'), ('#EF5A64', '오류', 'fault'), ('#759495', '알 수 없음', 'unknown')]
    sw = ''.join(f'<div class="swatch"><div style="background:{c}"></div><p><code>{c}</code><br>{n}<br><span class="muted">{u}</span></p></div>'
                 for c, n, u in colours)
    anims = ''.join([
        anim_card(1, '전환: STEERIX → MATRIX (원본)', '2.6초. STEERIX 심볼이 여섯 조각으로 흩어졌다가 MATRI 옆 X로 모입니다. SVG는 받은 원본 그대로입니다.',
                  video(D[1] / 'steerix-to-matrix.mp4', 'full'),
                  [('HTML로 보기', 'steerix-to-matrix.html', True), ('MP4', 'steerix-to-matrix.mp4', False),
                   ('GIF', 'steerix-to-matrix.gif', False), ('MOV 투명', 'steerix-to-matrix-transparent.mov', False),
                   ('SVG 원본', 'steerix-to-matrix.svg', False), ('MP4 초록 X', 'steerix-to-matrix-green-x.mp4', False),
                   ('GIF 초록 X', 'steerix-to-matrix-green-x.gif', False), ('MOV 투명 초록 X', 'steerix-to-matrix-green-x-transparent.mov', False),
                   ('SVG 초록 X', 'steerix-to-matrix-green-x.svg', False)]),
        anim_card(2, '전환: MATRIX → STEERIX', '2.6초. 원본을 거꾸로 재생합니다. MATRI가 I부터 사라지고 X가 흩어져 STEERIX 심볼로 모이며, STEERIX 글자가 오른쪽에서 들어옵니다.',
                  video(D[2] / 'matrix-to-steerix.mp4', 'full'),
                  [('HTML로 보기', 'matrix-to-steerix.html', True), ('MP4', 'matrix-to-steerix.mp4', False),
                   ('GIF', 'matrix-to-steerix.gif', False), ('MOV 투명', 'matrix-to-steerix-transparent.mov', False),
                   ('SVG', 'matrix-to-steerix.svg', False), ('MP4 초록 X', 'matrix-to-steerix-green-x.mp4', False),
                   ('GIF 초록 X', 'matrix-to-steerix-green-x.gif', False), ('MOV 투명 초록 X', 'matrix-to-steerix-green-x-transparent.mov', False),
                   ('SVG 초록 X', 'matrix-to-steerix-green-x.svg', False)]),
        anim_card(3, '로딩: MATRIX X → STEERIX X', '앱의 로딩 아이콘. 1.05초 멈춤 → 0.76초 동안 한 바퀴 돌며 STEERIX X 모양으로 바뀜 → 다시 MATRIX X로. 3.62초 반복.',
                  f'<img src="{href(D[3] / "loading-x-to-steerix-cyan.svg")}" alt="">'
                  f'<img src="{href(D[3] / "loading-x-to-steerix-green.svg")}" alt="">',
                  [('HTML로 보기', 'loading-x-to-steerix.html', True)] +
                  [(f'{f} {lab}', f'loading-x-to-steerix-{c}{suf}', False)
                   for c, lab in (('cyan', '하늘색'), ('white', '흰색'), ('green', '초록'))
                   for f, suf in (('SVG', '.svg'), ('MP4', '.mp4'), ('GIF', '.gif'), ('MOV 투명', '-transparent.mov'))]),
        anim_card(4, '로딩: MATRIX 글자의 X 회전', 'MATRI 옆의 X가 돌면서 STEERIX X로 바뀌었다 돌아옵니다(로고 원본 애니메이션). 3.62초 반복.',
                  f'<img class="wide" src="{href(D[4] / "loading-matrix-x-turn-green.svg")}" alt="">',
                  [('HTML로 보기', 'loading-matrix-x-turn.html', True)] +
                  [(f'{f} {lab}', f'loading-matrix-x-turn-{c}{suf}', False)
                   for c, lab in (('color', '하늘색 X'), ('green', '초록 X'), ('white', '흰색'))
                   for f, suf in (('SVG', '.svg'), ('MP4', '.mp4'), ('GIF', '.gif'), ('MOV 투명', '-transparent.mov'))]),
        anim_card(5, '로딩: STEERIX 회전', '1.8초 반복. 두 반쪽이 모였다가 한 바퀴 돌고 다시 벌어집니다. 외곽 라인 없이 면만 있습니다.',
                  f'<img src="{href(D[5] / "loading-steerix-spin-green.svg")}" alt="">'
                  f'<img src="{href(D[5] / "loading-steerix-spin-white.svg")}" alt="">',
                  [('HTML로 보기', 'loading-steerix-spin.html', True)] +
                  [(f'{f} {lab}', f'loading-steerix-spin-{c}{suf}', False)
                   for c, lab in (('green', '초록'), ('white', '흰색'))
                   for f, suf in (('SVG', '.svg'), ('MP4', '.mp4'), ('GIF', '.gif'), ('MOV 투명', '-transparent.mov'))]),
        anim_card(5, '로딩: STEERIX 코드비', '앱 첫 로딩 화면의 STEERIX. 같은 회전에 코드 글자가 흘러내립니다. 1.8초 반복.',
                  video(D[5] / 'loading-steerix-code-rain.mp4'),
                  [('HTML로 보기', 'loading-steerix-code-rain.html', True), ('MP4', 'loading-steerix-code-rain.mp4', False),
                   ('GIF', 'loading-steerix-code-rain.gif', False), ('MOV 투명', 'loading-steerix-code-rain-transparent.mov', False)]),
    ])
    fonts = Path('4-폰트')
    font_links = links([('STEERIX Logo 폰트 (TTF)', fonts / 'STEERIX-Logo-Regular.ttf', True),
                        ('MATRIX Logo 폰트 (TTF)', fonts / 'MATRIX-Logo-Regular.ttf', True),
                        ('UI 글꼴 IBM Plex 폴더', fonts / 'UI 글꼴 (IBM Plex)', False)])
    return f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>STEERIX MATRIX 브랜드</title>
<style>{CSS}</style>
</head>
<body>
<main>
<header>
  <div>
    <img src="{href(Path(L.DIRS['steerix-logo']) / 'steerix-logo-white.png')}" alt="STEERIX">
    <h1>STEERIX · MATRIX 브랜드 자료</h1>
    <p class="lead">로고, 색, 폰트, 애니메이션을 모두 이 폴더에 담았습니다. 각 링크를 누르면 파일이 열립니다. 로고 모양은 MATRIX 앱의 원본 로고 소스와 STEERIX→MATRIX 인트로 원본(2026-09-11)에서 그대로 가져왔습니다.</p>
  </div>
</header>

<h2>STEERIX</h2>
<p class="lead">PNG는 배경이 투명합니다(3200px, 심볼 2048px). AI·PDF·EPS·SVG는 벡터라서 크기를 키워도 깨지지 않습니다. AI는 일러스트레이터에서 바로 열립니다.</p>
<div class="grid">{steerix}</div>

<h2>MATRIX</h2>
<p class="lead">MATRIX의 X는 글자가 아니라 마크입니다. 초록 X는 앱의 ready 색 #00DB89입니다.</p>
<div class="grid">{matrix}{matrix_light}</div>

<h2>RobotSim</h2>
<p class="lead">STEERIX의 real-to-sim 서비스(robotsim.dev). 로고는 사이트 머리글 그대로입니다: 큐브 마크와 Inter Tight 글자, 머리글의 크기와 간격 그대로. RobotSim의 모든 화면, 영상, 이미지는 <b>Inter Tight</b>(제목·본문)와 <b>JetBrains Mono</b>(작은 라벨·수치) 두 글꼴로 통일합니다. 이름은 항상 RobotSim(R과 S만 대문자, 붙여 씀)으로 씁니다.</p>
<div class="grid">{robotsim}</div>
<div class="swatches">{rs_sw}</div>
<div class="rs"><div class="h">Send us your space.<br><span>Get it back sim-ready.</span></div><div class="b">Inter Tight 800 제목 · 400 본문. 로고의 RobotSim은 700, by Steerix는 500입니다.</div><div class="m">JETBRAINS MONO · SAMPLE IN 48 H · INTERNAL LAB DEMO</div>{rs_font_links}</div>

<h2>색</h2>
<p class="lead">로고는 흰색·검정이 기본이고, 초록과 상태 색은 MATRIX 앱에서 쓰는 값입니다.</p>
<div class="swatches">{sw}</div>

<h2>폰트</h2>
<p class="lead">로고 글자는 디자인된 모양이라 원래 폰트 파일이 없습니다. 그래서 로고 글자만 담은 폰트를 만들었습니다. STEERIX Logo에는 S T E R I X, MATRIX Logo에는 M A T R I와 X 마크가 들어 있고, 소문자로 쳐도 됩니다. 앱 화면의 글꼴은 IBM Plex Sans·Mono이며 무료 라이선스(OFL)입니다.</p>
<div class="tester">
  <input id="type" value="STEERIX" aria-label="미리보기 글자" maxlength="40">
  <div class="out s" id="outS">STEERIX</div>
  <div class="out m" id="outM">MATRIX</div>
  {font_links}
</div>

<h2>애니메이션</h2>
<p class="lead">HTML은 브라우저에서 바로 재생됩니다. MP4·GIF는 검은 배경, MOV는 배경이 투명해서 영상 편집에 바로 얹을 수 있습니다(ProRes 4444). SVG는 웹페이지에 이미지로 넣으면 그대로 움직입니다. 로딩 MP4는 약 10초 반복이고, GIF·MOV·SVG는 한 주기라 이어 붙이면 끊김 없이 반복됩니다.</p>
<div class="grid wide">{anims}</div>

<footer>2026-10-18 (RobotSim 추가 2026-10-19) · 원본: MATRIX 앱 web/src/brand (matrix-logo.js, steerix_loading_motion.cpp 이식본), web/public/brand/startup-intro.svg (STEERIX_to_MATRIX_Burst.svg)</footer>
</main>
<script>
const input = document.getElementById('type');
input.addEventListener('input', () => {{
  const t = input.value || ' ';
  document.getElementById('outS').textContent = t;
  document.getElementById('outM').textContent = t;
}});
</script>
</body>
</html>
'''


if __name__ == '__main__':
    out = Path(sys.argv[1]).expanduser()
    (out / '브랜드시트.html').write_text(build())
    print('ok')
