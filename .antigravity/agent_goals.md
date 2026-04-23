# Goal: Verified MapleLand Trade System

## 1. 핵심 프로세스
- **Auth:** 모든 유저는 Discord OAuth2를 통해 로그인해야 함.
- **Capture:** `getDisplayMedia`로 창을 선택한 후, 'PrintScreen'키 입력 시에만 해당 프레임을 캡처하여 서버로 전송.
- **Extraction:** 서버는 전송된 이미지에서 텍스트(아이템명, 옵션)를 추출하여 등록 폼에 자동 입력(Auto-fill) 기능을 제공해야 함.

## 2. 우선순위
1.  **Discord Login:** OAuth2 연동 및 세션 관리.
2.  **Stream Capture:** 실시간 스트림 연결 및 특정 키(Hot-key) 이벤트 리스너 구현.
3.  **OCR Pipeline:** 이미지에서 정밀한 아이템 수치 추출 알고리즘.

## 3. 버전별 구현목록
1. **v1:** Discord Login제외, 스냅샷한 이미지에서 텍스트를 추출해서 등록 폼에 자동입력 기능 및 테스트UI 구현