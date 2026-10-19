<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="1-STEERIX/%EB%A1%9C%EA%B3%A0%28%EC%8B%AC%EB%B3%BC%2B%EA%B8%80%EC%9E%90%29/steerix-logo-white.png">
    <img src="1-STEERIX/%EB%A1%9C%EA%B3%A0%28%EC%8B%AC%EB%B3%BC%2B%EA%B8%80%EC%9E%90%29/steerix-logo-black.png" alt="STEERIX" width="420">
  </picture>
</p>

# STEERIX · MATRIX · RobotSim 브랜드 자료

로고, 색, 폰트, 전환·로딩 애니메이션을 한곳에 모았습니다. 저장소를 내려받아 `브랜드시트.html`을 브라우저로 열면 전체를 미리 보고 각 파일을 바로 열 수 있습니다. 파일별 설명은 [안내.md](%EC%95%88%EB%82%B4.md)에 있습니다.

| STEERIX → MATRIX (원본 인트로) | MATRIX → STEERIX |
|---|---|
| <img src="3-%EC%95%A0%EB%8B%88%EB%A9%94%EC%9D%B4%EC%85%98/1-%EC%A0%84%ED%99%98-STEERIX%EC%97%90%EC%84%9C-MATRIX%EB%A1%9C/steerix-to-matrix.gif" width="420" alt="STEERIX to MATRIX"> | <img src="3-%EC%95%A0%EB%8B%88%EB%A9%94%EC%9D%B4%EC%85%98/2-%EC%A0%84%ED%99%98-MATRIX%EC%97%90%EC%84%9C-STEERIX%EB%A1%9C/matrix-to-steerix.gif" width="420" alt="MATRIX to STEERIX"> |

| MATRIX X → STEERIX X | MATRIX 글자 X 회전 | STEERIX 회전 | STEERIX 코드비 |
|---|---|---|---|
| <img src="3-%EC%95%A0%EB%8B%88%EB%A9%94%EC%9D%B4%EC%85%98/3-%EB%A1%9C%EB%94%A9-MATRIX%20X%EC%97%90%EC%84%9C-STEERIX%20X%EB%A1%9C/loading-x-to-steerix-cyan.gif" width="160" alt=""> | <img src="3-%EC%95%A0%EB%8B%88%EB%A9%94%EC%9D%B4%EC%85%98/4-%EB%A1%9C%EB%94%A9-MATRIX%20%EA%B8%80%EC%9E%90%20X%20%ED%9A%8C%EC%A0%84/loading-matrix-x-turn-green.gif" width="260" alt=""> | <img src="3-%EC%95%A0%EB%8B%88%EB%A9%94%EC%9D%B4%EC%85%98/5-%EB%A1%9C%EB%94%A9-STEERIX%20%ED%9A%8C%EC%A0%84%28%EC%A0%84%EB%B6%80%29/loading-steerix-spin-green.gif" width="160" alt=""> | <img src="3-%EC%95%A0%EB%8B%88%EB%A9%94%EC%9D%B4%EC%85%98/5-%EB%A1%9C%EB%94%A9-STEERIX%20%ED%9A%8C%EC%A0%84%28%EC%A0%84%EB%B6%80%29/loading-steerix-code-rain.gif" width="160" alt=""> |

## 들어 있는 것

- **1-STEERIX**: 로고(심볼+글자), 심볼(그림만), 글자만, 앱 아이콘. PNG(배경 투명) · SVG · AI · PDF · EPS
- **2-MATRIX**: 로고(MATRIX 전체 글자), X 로고만. 흰색 · 검정 · 초록 X(#00DB89)
- **5-RobotSim**: robotsim.dev 머리글과 같은 큐브 마크 + RobotSim 로고(+ by Steerix). 민트 · 흰색 · 검정 · 검정 + 민트 마크. PNG · SVG · PDF · AI
- **3-애니메이션**: 전환 2종과 로딩 3종. HTML · MP4 · GIF · 투명 MOV(ProRes 4444) · SVG
- **4-폰트**:
  - STEERIX Logo, MATRIX Logo: 로고 글자만 담은 폰트
  - IBM Plex: 앱 화면 글꼴, OFL 라이선스
  - RobotSim 글꼴: Inter Tight · JetBrains Mono (가변 TTF), OFL 라이선스

## 원본

로고 모양은 새로 그리지 않았습니다. MATRIX 저장소의 원본에서 좌표를 그대로 가져왔습니다.

- `web/src/brand`: matrix-logo.js와 steerix_loading_motion.cpp 이식본
- `web/public/brand/startup-intro.svg`: STEERIX_to_MATRIX_Burst.svg

MATRIX → STEERIX 전환은 원본이 없어서, 원본 인트로를 거꾸로 재생해 만들었습니다.

## 다시 만들기

`tools/build.sh`를 실행하면 원본에서 폴더 전체를 다시 만듭니다. 필요한 것:

- MATRIX 저장소: `~/matrix_reboot/web`
- Playwright가 내려받은 headless Chromium
- ffmpeg
- Python: websockets · fontTools · Pillow
