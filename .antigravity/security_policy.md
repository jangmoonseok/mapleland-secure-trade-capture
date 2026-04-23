# Security & Integrity Policy

- **No File Input:** 일반적인 파일 선택 업로드(`<input type="file">`)는 절대 허용하지 않음.
- **Verified Metadata:** 캡처 시점의 타임스탬프와 디스코드 유저 ID를 이미지 메타데이터 또는 서버 DB와 대조.
- **OCR Validation:** 추출된 스탯이 게임 내 최대 수치를 초과하면 허위 매물로 간주하고 차단.