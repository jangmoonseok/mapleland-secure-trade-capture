# Capture & Security Technical Spec

## 1. Window Detection
- `pygetwindow` 또는 `win32gui` 라이브러리를 사용하여 "MapleLand" 프로세스를 탐지.
- 게임 창의 절대 좌표를 계산하고, 해당 영역만 `BitBlt` 또는 `PrintWindow` API로 캡처.
- **중요:** 게임 화면이 최소화되어 있거나 다른 창에 가려진 경우 캡처를 거부하거나 경고 표시.

## 2. Image Tamper-Proof (변조 방지)
- 캡처 시점에 유저 ID + 현재 시각 + 고유 기기 값을 조합하여 HMAC-SHA256 서명 생성.
- 서명 데이터를 이미지의 LSB(Least Significant Bit)에 스테가노그래피 방식으로 숨기거나 헤더에 삽입.

## 3. 전용 업로드
- 유저가 '내보내기'를 누르면, 로컬 파일 탐색기를 거치지 않고 서버 API로 `multipart/form-data` 전송.